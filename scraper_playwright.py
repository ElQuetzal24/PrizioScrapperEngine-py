import asyncio
import csv
from playwright.async_api import async_playwright
from pathlib import Path
from datetime import datetime

ARCHIVO_CSV = "productos.csv"
CATEGORIA_URL = "https://www.walmart.co.cr/articulos-para-el-hogar?page="
MAX_PAGINAS = 50

async def scroll_hasta_cargar_todos(page):
    productos_previos = -1
    ciclos_sin_cambio = 0
    max_sin_cambio = 4
    max_ciclos = 20 # máximo de intentos para evitar bucles infinitos
    velocidad_scroll = 800  # milisegundos entre ciclos

    for ciclo in range(max_ciclos):
        # Scroll fuerte al fondo (como "End")
        await page.keyboard.press("End")
        await page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
        await page.wait_for_timeout(velocidad_scroll)

        # Contar productos actuales
        productos_actuales = await page.locator(".vtex-search-result-3-x-galleryItem").count()

        # Mostrar solo si hay cambio o cada 5 ciclos
        if productos_actuales != productos_previos or ciclo % 5 == 0:
            print(f"🔄 Scroll {ciclo+1}: {productos_actuales} productos visibles")

        # Control de cambio
        if productos_actuales == productos_previos:
            ciclos_sin_cambio += 1
        else:
            ciclos_sin_cambio = 0
            productos_previos = productos_actuales

        # Salir si se estanca
        if ciclos_sin_cambio >= max_sin_cambio:
            print(f"✅ Scroll finalizado: {productos_actuales} productos cargados (sin cambios en {max_sin_cambio} ciclos)")
            break

    else:
        print(f"⚠️ Fin de scroll por límite de ciclos ({max_ciclos}). Productos detectados: {productos_actuales}")



async def extraer_productos(page, pagina, visto_urls):
    url = f"{CATEGORIA_URL}{pagina}"
    await page.goto(url, timeout=60000)
    await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=15000)
    await scroll_hasta_cargar_todos(page)

    #
    productos = []
 

    # Capturar todos los elementos de una sola vez (para evitar reevaluación del DOM)
    elements = await page.query_selector_all(".vtex-search-result-3-x-galleryItem")
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')

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


        precio_node = await item.query_selector("[class*=price]")
        precio = await precio_node.text_content() if precio_node else None

        productos.append({
            "nombre": nombre,
            "precio": precio.strip().replace("₡", "").replace(",", "") if precio else "N/A",
            "sku": "N/A",
            "url": url,
            "fecha": fecha_hoy,
            "imagen": img_url
        })
    return productos
    # 

async def guardar_csv(productos):
    archivo_existente = Path(ARCHIVO_CSV).exists()
    with open(ARCHIVO_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nombre", "precio", "sku", "url", "fecha", "imagen"])
        if not archivo_existente:
            writer.writeheader()
        for p in productos:
            writer.writerow(p)

async def main():
    ultima_pagina_exitosa = 1
    try:
        with open("ultima_pagina.txt", "r") as f:
            ultima_pagina_exitosa = int(f.read().strip())
    except:
        pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        visto_urls = set()
        for pagina in range(ultima_pagina_exitosa, MAX_PAGINAS + 1):
            try:
                print(f"🌀 Página {pagina}")
                productos = await extraer_productos(page, pagina, visto_urls)
                print(f"✅ Productos extraídos: {len(productos)}")
                await guardar_csv(productos)

                with open("ultima_pagina.txt", "w") as f:
                    f.write(str(pagina + 1))

            except Exception as e:
                print(f"❌ Error en la página {pagina}: {e}")
                break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
