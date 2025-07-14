import re
from datetime import datetime
from navegador import scroll_hasta_cargar_todos, safe_text_content
from db import guardar_productos_scrapeados
from loguru import logger

def extraer_precios(texto):
    precios = re.findall(r"₡\s*\d[\d\.]*", texto)
    normalizados = []
    for p in precios:
        p = p.replace("₡", "").replace(".", "").replace(",", ".").strip()
        try:
            normalizados.append(float(p))
        except:
            pass

    if len(normalizados) >= 2:
        return normalizados[1], normalizados[0]
    elif len(normalizados) == 1:
        return normalizados[0], normalizados[0]
    else:
        return 0.0, 0.0

async def extraer_marca_detallada(page, url_producto):
    try:
        await page.goto(url_producto, timeout=30000)
        await page.wait_for_timeout(1500)

        filas = await page.query_selector_all("table tr")
        for fila in filas:
            th = await fila.query_selector("th")
            td = await fila.query_selector("td")
            th_text = await safe_text_content(th)
            if th_text and "marca" in th_text.lower():
                td_text = await safe_text_content(td)
                marca = td_text.strip()
                if marca:
                    print(f" Marca desde tabla: {marca}")
                    return marca

        dts = await page.query_selector_all("dt")
        for dt in dts:
            dt_text = await safe_text_content(dt)
            if dt_text and "marca" in dt_text.lower():
                dd = await dt.evaluate_handle("el => el.nextElementSibling")
                marca = await safe_text_content(dd)
                if marca:
                    print(f" Marca desde definiciones: {marca}")
                    return marca.strip()

        return "N/A"
    except Exception as e:
        print(f" Error extrayendo marca en detalle: {e}")
        return "N/A"

async def extraer_productos(page, url_categoria, categoria, visto_urls):
    await page.goto(url_categoria, timeout=30000)
    await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=10000)
    await scroll_hasta_cargar_todos(page)

    productos = []
    elements = await page.query_selector_all(".vtex-search-result-3-x-galleryItem")
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')

    for item in elements:
        link = await item.query_selector("a")
        href = await link.get_attribute("href") if link else None
        if not href:
            continue

        url = f"https://www.walmart.co.cr{href}"
        if url in visto_urls:
            continue

        visto_urls.add(url)

        img_node = await item.query_selector("img")
        img_url = await img_node.get_attribute("src") if img_node else None
        img_url = img_url.strip() if img_url and isinstance(img_url, str) else "N/A"

        marca_node = await item.query_selector(".vtex-product-summary-2-x-brandName")
        marca = await safe_text_content(marca_node)
        marca = marca.strip() if marca else ""

        if not marca:
            nueva_pestana = await page.context.new_page()
            marca = await extraer_marca_detallada(nueva_pestana, url)
            await nueva_pestana.close()

        if not marca or marca.strip().lower() == "agregar":
            marca_node = await item.query_selector(".vtex-product-summary-2-x-productBrand")
            marca = await safe_text_content(marca_node)

        marca = marca.strip() if marca else "N/A"

        nombre = await item.query_selector(".vtex-product-summary-2-x-productBrand")
        nombre = await nombre.text_content() if nombre else None
        if not nombre or nombre.strip().lower() == "agregar":
            nombre_node = await item.query_selector(".vtex-product-summary-2-x-productName")
            nombre = await nombre_node.text_content() if nombre_node else None
        if not nombre or nombre.strip().lower() == "agregar":
            nombre_node = await item.query_selector("a span")
            nombre = await nombre_node.text_content() if nombre_node else None
        if not nombre or nombre.strip().lower() == "agregar":
            nombre = await item.inner_text()
        nombre = nombre.strip() if nombre and isinstance(nombre, str) else "N/A"

        precio_node = await item.query_selector("[class*=price]")
        if precio_node:
            texto_precio = await precio_node.text_content()
            precio_actual, precio_anterior = extraer_precios(texto_precio)
        else:
            precio_actual = precio_anterior = 0.0

        productos.append({
            "nombre": nombre,
            "marca": marca,
            "precio": precio_actual,
            "precio_anterior": precio_anterior,
            "sku": "N/A",
            "url": url,
            "fecha": fecha_hoy,
            "imagen": img_url,
            "categoria": categoria
        })

    return productos

async def procesar_categoria(page, categoria, urls_vistas, semaforo):
    url_categoria = f"https://www.walmart.co.cr/{categoria}"
    async with semaforo:
        try:
            logger.info(f"Procesando categoría: {categoria}")
            productos = await extraer_productos(page, url_categoria, categoria, urls_vistas)
            if productos:
                guardar_productos_scrapeados(productos)
            else:
                logger.warning(f"No se encontraron productos en la categoría: {categoria}")
        except Exception as e:
            logger.error(f"Error procesando categoría {categoria}: {e}")
        finally:
            await page.close()
