import asyncio
from playwright.async_api import async_playwright
from extractor import extraer_datos_producto
from db import guardar_productos_scrapeados
from logger import logger

BASE_URL = "https://tienda.pequenomundo.com"

async def procesar_categoria(ruta_categoria: str, sem: asyncio.Semaphore):
    async with sem:
        logger.info(f"Procesando categoría: {ruta_categoria}")
        productos_extraidos = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/89.0.4389.82 Safari/537.36",
                    viewport={"width": 1280, "height": 1024},
                    locale="es-CR"
                )
                page = await context.new_page()

                url = f"{BASE_URL}/{ruta_categoria}.html?product_list_limit=all"
                await page.goto(url)

                await page.wait_for_selector("li.product-item", timeout=20000)

                for _ in range(5):
                    await page.mouse.wheel(0, 4000)
                    await page.wait_for_timeout(1000)

                items = await page.query_selector_all("li.product-item")
                logger.info(f"Se encontraron {len(items)} elementos en {ruta_categoria}")

                for item in items:
                    try:
                        producto = await extraer_datos_producto(item, ruta_categoria)
                        if producto:
                            productos_extraidos.append(producto)
                    except Exception as e:
                        logger.error(f"Error extrayendo producto: {e}")

                await browser.close()

        except Exception as e:
            logger.error(f"Error procesando categoría {ruta_categoria}: {e}")
            return

        await guardar_productos_scrapeados(productos_extraidos)
        logger.info(f"{len(productos_extraidos)} productos guardados de {ruta_categoria}")
