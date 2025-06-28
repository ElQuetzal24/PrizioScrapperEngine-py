import asyncio
import csv
from playwright.async_api import async_playwright
from pathlib import Path

ARCHIVO_CSV = "productos.csv"
CATEGORIA_URL = "https://www.walmart.co.cr/articulos-para-el-hogar?page="
MAX_PAGINAS = 50

async def scroll_hasta_cargar_todos(page):
    productos_previos = -1
    ciclos_sin_cambio = 0
    max_sin_cambio = 4
    max_ciclos = 30
    velocidad_scroll = 1000  # milisegundos entre ciclos

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



async def extraer_productos(page, pagina):
    url = f"{CATEGORIA_URL}{pagina}"
    await page.goto(url, timeout=60000)
    await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=15000)
    await scroll_hasta_cargar_todos(page)

    items = page.locator(".vtex-search-result-3-x-galleryItem")
    total = await items.count()
    productos = []
    visto_urls = set()

    for i in range(total):
        item = items.nth(i)

        # Obtener URL única
        link = await item.locator("a").first.get_attribute("href")
        if not link:
            continue
        url = f"https://www.walmart.co.cr{link}"

        if url in visto_urls:
            continue  # producto duplicado en esta página
        visto_urls.add(url)

        # Extraer nombre robusto
        nombre = await item.locator(".vtex-product-summary-2-x-productBrand").first.text_content()
        if not nombre or nombre.strip().lower() in ["agregar", ""]:
            nombre = await item.locator(".vtex-product-summary-2-x-productName").first.text_content()
        if not nombre or nombre.strip().lower() in ["agregar", ""]:
            nombre = await item.locator("a span").first.text_content()
        if not nombre or nombre.strip().lower() in ["agregar", ""]:
            nombre = await item.inner_text()
        nombre = nombre.strip() if nombre else "N/A"

        precio = await item.locator("[class*=price]").first.text_content()

        productos.append({
            "nombre": nombre,
            "precio": precio.strip().replace("₡", "").replace(",", "") if precio else "N/A",
            "sku": "N/A",
            "url": url
        })


        # Nombre robusto: varios intentos
        nombre = await item.locator(".vtex-product-summary-2-x-productBrand").first.text_content()
        if not nombre or nombre.strip().lower() in ["agregar", ""]:
            nombre = await item.locator(".vtex-product-summary-2-x-productName").first.text_content()
        if not nombre or nombre.strip().lower() in ["agregar", ""]:
            nombre = await item.locator("a span").first.text_content()
        if not nombre or nombre.strip().lower() in ["agregar", ""]:
            nombre = await item.inner_text()

        nombre = nombre.strip() if nombre else "N/A"

        precio = await item.locator("[class*=price]").first.text_content()
        link = await item.locator("a").first.get_attribute("href")

        productos.append({
            "nombre": nombre,
            "precio": precio.strip().replace("₡", "").replace(",", "") if precio else "N/A",
            "sku": "N/A",
            "url": f"https://www.walmart.co.cr{link}" if link else "N/A"
        })
    return productos

async def guardar_csv(productos):
    archivo_existente = Path(ARCHIVO_CSV).exists()
    with open(ARCHIVO_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nombre", "precio", "sku", "url"])
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

        for pagina in range(ultima_pagina_exitosa, MAX_PAGINAS + 1):
            try:
                print(f"🌀 Página {pagina}")
                productos = await extraer_productos(page, pagina)
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
