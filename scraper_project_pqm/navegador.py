import asyncio
from playwright.async_api import async_playwright
from db import guardar_productos_scrapeados
from db import guardar_productos_scrapeados_masivo
from logger import logger

BASE = "https://tienda.pequenomundo.com"

async def procesar_categoria(ruta: str, sem: asyncio.Semaphore):
    url = f"{BASE}/{ruta}.html?product_list_limit=all"
    async with sem:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="es-CR"
            )
            page = await context.new_page()
            logger.info(f"Procesando: /{ruta}")
            try:
                await page.goto(url, timeout=60000)
                for _ in range(5):
                    await page.mouse.wheel(0, 4000)
                    await page.wait_for_timeout(1000)

                await page.wait_for_selector("li.product-item", timeout=20000)
            except Exception as e:
                logger.warning(f"Sin productos o error en /{ruta} → {e}")
                await browser.close()
                return

            productos = await page.query_selector_all("li.product-item")
            logger.info(f"{len(productos)} productos en /{ruta}")

            productos_data = []
            for producto in productos:
                try:
                    nombre_el = await producto.query_selector("a.product-item-link")
                    precio_el = await producto.query_selector("span.price")

                    nombre = (await nombre_el.text_content()).strip() if nombre_el else "N/A"
                    precio = (await precio_el.text_content()).strip() if precio_el else "N/A"

                    href = await nombre_el.get_attribute("href") if nombre_el else ""
                    url_final = href if href.startswith("http") else BASE + href
                    slug = href.strip().split("/")[-1].replace(".html", "") if href else "N/A"

                    imagen_el = await producto.query_selector("img.product-image-photo")
                    imagen_url = ""

                    if imagen_el:
                        posibles_atributos = ["src", "data-src", "data-original", "data-srcset", "data-image-src"]
                        for attr in posibles_atributos:
                            valor = await imagen_el.get_attribute(attr) or ""
                            if valor and "pixel.jpg" not in valor and valor.startswith("http"):
                                imagen_url = valor.strip()
                                if "/cache/" in imagen_url:
                                    partes = imagen_url.split("/cache/")
                                    if len(partes) > 1:
                                        imagen_url = "/".join(partes[0:1]) + "/" + "/".join(partes[1].split("/")[1:])
                                break
                        if "pixel.jpg" in imagen_url or not imagen_url.endswith(".jpg"):
                            imagen_url = ""

                    logger.info("─────────────")
                    logger.info(f" NOMBRE: {nombre}")
                    logger.info(f" PRECIO: {precio}")
                    logger.info(f" URL   : {url_final}")
                    logger.info(f" SLUG  : {slug}")

                    productos_data.append({
                        "nombre": nombre,
                        "precio": precio,
                        "url": url_final,
                        "slug": slug,
                        "categoria": ruta,
                        "imagen": imagen_url
                    })
                except Exception as ex:
                    logger.error(f"Error al procesar producto individual: {ex}")

            await browser.close()

            if productos_data:
                
 
                guardar_productos_scrapeados_masivo(productos_data)
                logger.info(f"{len(productos_data)} productos guardados de {ruta}")
