import asyncio
import csv
from playwright.async_api import async_playwright
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import re
from loguru import logger

from repositorio.sql_server import guardar_en_bd
from repositorio.sql_server import guardar_en_bd2   


ARCHIVO_CSV = "productos.csv"
CATEGORIAS = [
    "articulos-para-el-hogar"
    ,"juguetes","deportes","ropa-y-zapateria","lo-nuevo","electronica","limpieza","abarrotes","higiene-y-belleza"
    ,"bebes-y-ninos","lacteos","jugos-y-bebidas","carnes-y-pescados","cervezas-vinos-y-licores","embutidos","panaderia-y-tortilleria"
    ,"alimentos-congelados","frutas-y-verduras","mascota","farmacia"
    #,"rebajas"
]


MAX_PAGINAS = 50

async def scroll_hasta_cargar_todos(page):
    productos_previos = -1
    ciclos_sin_cambio = 0
    max_sin_cambio = 4
    max_ciclos = 40 # máximo de intentos para evitar bucles infinitos
    velocidad_scroll = 400  # milisegundos entre ciclos

    for ciclo in range(max_ciclos):
        # Scroll fuerte al fondo (como "End")
        await page.keyboard.press("End")
        await page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
        await page.mouse.wheel(0, 2000)
        await page.wait_for_timeout(velocidad_scroll)

        # Contar productos actuales
        productos_actuales = await page.locator(".vtex-search-result-3-x-galleryItem").count()

        # Mostrar solo si hay cambio o cada 5 ciclos
        if productos_actuales != productos_previos or ciclo % 5 == 0:
            logger.debug(f"Scroll {ciclo+1}: {productos_actuales} productos visibles")

        # Control de cambio
        if productos_actuales == productos_previos:
            ciclos_sin_cambio += 1
        else:
            ciclos_sin_cambio = 0
            productos_previos = productos_actuales

        # Salir si se estanca
        if ciclos_sin_cambio >= max_sin_cambio:
            print(f" Scroll finalizado: {productos_actuales} productos cargados (sin cambios en {max_sin_cambio} ciclos)")
            break

    else:
        print(f" Fin de scroll por límite de ciclos ({max_ciclos}). Productos detectados: {productos_actuales}")

async def procesar_categoria(page, categoria, visto_urls, semaforo):
    async with semaforo:
        logger.info(f"Procesando categoría: {categoria}")
        for pagina in range(1, MAX_PAGINAS + 1):
            try:
                url_categoria = f"https://www.walmart.co.cr/{categoria}?page={pagina}"
                print(f" Página {pagina} → {url_categoria}")
                productos = await extraer_productos(page, url_categoria, categoria, visto_urls)

                if not productos:
                    print(f" No se extrajeron productos de {categoria} en la página {pagina}.")
                    break

                print(f" Productos extraídos: {len(productos)}")
                guardar_en_bd2(productos)

            except Exception as e:
                print(f" Error en la página {pagina}: {e}")
                break

async def procesar_categoria_scroll(page, categoria, visto_urls, semaforo):
    async with semaforo:
        url_categoria = f"https://www.walmart.co.cr/{categoria}"
        print(f"\n Procesando categoría: {categoria}")
        try:
            productos = await extraer_productos(page, url_categoria, categoria, visto_urls)
            if productos:
                print(f" Productos extraídos: {len(productos)}")
                guardar_en_bd2(productos)
            else:
                print(" No se extrajeron productos")
        except Exception as e:
            logger.error(f"Error en categoría {categoria}: {e}")


async def safe_text_content(node):
    if node is None:
        return ""
    try:
        return await node.text_content()
    except Exception as e:
        print(f" Error al obtener text_content: {e}")
        return ""

def extraer_precios(texto):
    """
    Extrae precio_actual y precio_anterior del texto si existen dos precios.
    Si hay solo uno, ambos campos serán iguales.
    """
    # Extraer todos los valores numéricos con ₡ incluido
    precios = re.findall(r"₡\s*\d[\d\.]*", texto)

    # Normalizar: quitar ₡ y puntos de miles, dejar solo coma decimal si existiera
    normalizados = []
    for p in precios:
        p = p.replace("₡", "").replace(".", "").replace(",", ".").strip()
        try:
            normalizados.append(float(p))
        except:
            pass

    if len(normalizados) >= 2:
        return normalizados[1], normalizados[0]  # nuevo, anterior
    elif len(normalizados) == 1:
        return normalizados[0], normalizados[0]
    else:
        return 0.0, 0.0

async def extraer_marca_detallada(page, url_producto):
    try:
        await page.goto(url_producto, timeout=30000)

        # Esperar carga básica
        await page.wait_for_timeout(1500)

        # Intentar extraer desde tabla técnica
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

        # Otra posible estructura: definición <dt>Marca</dt><dd>Sony</dd>
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
        logger.exception("Error extrayendo marca en detalle")
        return "N/A"

async def extraer_productos(page, url_categoria, categoria, visto_urls):
    await page.goto(url_categoria, timeout=30000)
    await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=10000)
    await scroll_hasta_cargar_todos(page)

    #
    productos = []
 

    # Capturar todos los elementos de una sola vez (para evitar reevaluación del DOM)
    elements = await page.query_selector_all(".vtex-search-result-3-x-galleryItem")
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    # Deducir la categoría a partir de la URL
    

    for item in elements:
        link = await item.query_selector("a")
        href = await link.get_attribute("href") if link else None
        if not href:
            continue

        url = f"https://www.walmart.co.cr{href}"
        if url in visto_urls:
            continue  # ya procesado

        visto_urls.add(url)

        # Extraer URL de imagen principal
        img_node = await item.query_selector("img")
        img_url = await img_node.get_attribute("src") if img_node else None
        img_url = img_url.strip() if img_url and isinstance(img_url, str) else "N/A"

        # Extraer marca desde la galería
        marca_node = await item.query_selector(".vtex-product-summary-2-x-brandName")
        marca = await safe_text_content(marca_node)
        marca = marca.strip() if marca else ""

        # Fallback si no hay marca: entrar al detalle del producto
        if not marca:
            nueva_pestana = await page.context.new_page()
            marca = await extraer_marca_detallada(nueva_pestana, url)
            await nueva_pestana.close()

        # Fallback si no está en .brandName
        if not marca or marca.strip().lower() == "agregar":
            marca_node = await item.query_selector(".vtex-product-summary-2-x-productBrand")
            marca = await safe_text_content(marca_node)

        marca = marca.strip() if marca else "N/A"


        # Extraer nombre robusto
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


        # Obtener nodo del precio y extraer precios
        precio_node = await item.query_selector("[class*=price]")
        if precio_node:
            texto_precio = await precio_node.text_content()
            precio_actual, precio_anterior = extraer_precios(texto_precio)
        else:
            precio_actual = precio_anterior = 0.0



        productos.append({
            "nombre": nombre,
            "marca": marca,  #  nuevo campo
            "precio": precio_actual,
            "precio_anterior": precio_anterior,
            "sku": "N/A",
            "url": url,
            "fecha": fecha_hoy,
            "imagen": img_url,
            "categoria": categoria
        })

    return productos
    # 

async def guardar_csv(productos):
    archivo_existente = Path(ARCHIVO_CSV).exists()
    with open(ARCHIVO_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nombre", "precio", "sku", "url", "fecha", "imagen", "categoria"])
        if not archivo_existente:
            writer.writeheader()
        for p in productos:
            writer.writerow(p)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tareas = []
        visto_urls = set()
        semaforo = asyncio.Semaphore(2)  #  máximo 3 tareas concurrentes
        for categoria in CATEGORIAS:
            page = await browser.new_page()

            tareas.append(procesar_categoria_scroll(page, categoria, visto_urls,semaforo))
    
        await asyncio.gather(*tareas)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
