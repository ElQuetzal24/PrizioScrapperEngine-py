
import asyncio
import re
import pyodbc
from datetime import datetime
from playwright.async_api import async_playwright

BASE_URL = "https://www.walmart.co.cr"
CATEGORIA_PATH = "/articulos-para-el-hogar"
PAGINA_URL = f"{BASE_URL}{CATEGORIA_PATH}?page={{}}"
FUENTE = "WalmartCR"

CONN_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=scrap_db;"
    "Trusted_Connection=yes;"
)

def parsear_precio(pstr):
    try:
        limpio = pstr.replace("₡", "").replace(".", "").replace(",", "").strip()
        return float(limpio)
    except:
        return 0.0

def guardar_en_bd(productos, page_number):
    try:
        conn = pyodbc.connect(CONN_STRING)
        cursor = conn.cursor()
        print(f"[DB] Insertando {len(productos)} productos de la página {page_number}...")

        cursor.executemany("""
            INSERT INTO dbo.Producto (FechaCreacion, UsuarioCreacion, Estado, Nombre, SKU, Fuente, Precio, ImagenUrl, Marca, Categoria)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, productos)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DB] Página {page_number} guardada con éxito.")
    except Exception as e:
        print(f"[DB Error] Página {page_number}: {e}")

async def scroll_hasta_cargar_todos(page):
    productos_antes = 0
    while True:
        await page.mouse.wheel(0, 2000)
        await page.wait_for_timeout(1500)
        productos_actuales = await page.locator(".vtex-search-result-3-x-galleryItem").count()
        if productos_actuales == productos_antes:
            break
        productos_antes = productos_actuales

async def procesar_pagina(context, page_number):
    page = await context.new_page()
    await page.goto(PAGINA_URL.format(page_number), timeout=60000)
    await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=15000)
    await scroll_hasta_cargar_todos(page)

    productos_raw = await page.locator(".vtex-search-result-3-x-galleryItem").element_handles()
    if not productos_raw:
        await page.close()
        return False

    resultados = []

    for p_item in productos_raw:
        try:
            nombre_el = await p_item.query_selector(".vtex-product-summary-2-x-productBrand")
            nombre = await nombre_el.inner_text() if nombre_el else "N/A"

            img_el = await p_item.query_selector("img")
            img_url = await img_el.get_attribute("src") if img_el else None

            link_el = await p_item.query_selector("a")
            href = await link_el.get_attribute("href") if link_el else None
            if not href:
                continue

            url = f"{BASE_URL}{href}" if href.startswith("/") else href

            product_page = await context.new_page()
            await product_page.goto(url, timeout=30000)
            await product_page.wait_for_timeout(2000)

            try:
                price_el = await product_page.query_selector(".vtex-store-components-3-x-price_sellingPrice span")
                raw_price = await price_el.inner_text() if price_el else "0"
                precio = parsear_precio(raw_price)
            except:
                precio = 0.0

            try:
                await product_page.wait_for_selector(".vtex-store-components-3-x-productReference", timeout=5000)
                html = await product_page.content()
                match = re.search(r">(\d{11,14})</span>\s*<h1", html)
                if match:
                    sku = match.group(1)
                else:
                    posibles = re.findall(r">\s*(\d{11,14})\s*<", html)
                    sku = posibles[0] if posibles else "N/A"
            except:
                sku = "N/A"

            try:
                marca_el = await product_page.query_selector("meta[name='brand']")
                marca = await marca_el.get_attribute("content") if marca_el else None
            except:
                marca = None

            try:
                breadcrumb = await product_page.locator("nav[aria-label='breadcrumb'] li a").all_inner_texts()
                categoria = breadcrumb[-2] if len(breadcrumb) >= 2 else None
            except:
                categoria = None

            await product_page.close()
            resultados.append((
                datetime.now(), "scraper", 1, nombre.strip(), sku.strip(), FUENTE,
                precio, img_url, marca, categoria
            ))

        except Exception as e:
            print("[Error] Producto:", e)

    await page.close()

    if resultados:
        guardar_en_bd(resultados, page_number)
    return True

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        context = await browser.new_context(ignore_https_errors=True)

        page_num = 1
        while True:
            tiene_productos = await procesar_pagina(context, page_num)
            if not tiene_productos:
                break
            page_num += 1

        await browser.close()
        print("[Info] Scraping completo")

asyncio.run(main())
