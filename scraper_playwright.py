import asyncio
import csv
from playwright.async_api import async_playwright
from pathlib import Path

ARCHIVO_CSV = "productos.csv"
CATEGORIA_URL = "https://www.walmart.co.cr/articulos-para-el-hogar?page="
MAX_PAGINAS = 50

async def scroll_hasta_cargar_todos(page):
    productos_antes = 0
    while True:
        await page.mouse.wheel(0, 2000)
        await page.wait_for_timeout(1500)
        productos_actuales = await page.locator(".vtex-search-result-3-x-galleryItem").count()
        if productos_actuales == productos_antes:
            break
        productos_antes = productos_actuales

async def extraer_productos(page, pagina):
    url = f"{CATEGORIA_URL}{pagina}"
    await page.goto(url, timeout=60000)
    await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=15000)
    await scroll_hasta_cargar_todos(page)

    items = page.locator(".vtex-search-result-3-x-galleryItem")
    total = await items.count()
    productos = []

    for i in range(total):
        item = items.nth(i)

        # Nombre: probar múltiples fuentes de texto visibles
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
