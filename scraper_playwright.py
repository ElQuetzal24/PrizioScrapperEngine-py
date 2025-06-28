import asyncio
import re
import pyodbc
from playwright.async_api import async_playwright

CATEGORIA_URL = "https://www.walmart.co.cr/articulos-para-el-hogar"

# CONEXIÓN A SQL SERVER
conn = pyodbc.connect(
      "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=scrap_db;"
            "Trusted_Connection=yes;"
)
cursor = conn.cursor()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        await page.goto(CATEGORIA_URL, timeout=30000)

        for _ in range(10):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(1000)

        await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=15000)
        productos = await page.locator(".vtex-search-result-3-x-galleryItem").element_handles()

        for p_item in productos:
            try:
                nombre_el = await p_item.query_selector(".vtex-product-summary-2-x-productBrand")
                nombre = await nombre_el.inner_text() if nombre_el else "N/A"

                link_el = await p_item.query_selector("a")
                href = await link_el.get_attribute("href") if link_el else None
                if not href:
                    continue

                url = f"https://www.walmart.co.cr{href}" if href.startswith("/") else href

                product_page = await context.new_page()
                await product_page.goto(url, timeout=30000)
                await product_page.wait_for_timeout(2000)

                try:
                    price_el = await product_page.query_selector(".vtex-store-components-3-x-price_sellingPrice span")
                    raw_price = await price_el.inner_text() if price_el else "0"
                    price_clean = raw_price.replace("₡", "").replace(".", "").replace(",", "").strip()
                    precio = float(price_clean)
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

                await product_page.close()

                print(f"✔ {nombre} | ₡{precio:,.0f} | SKU: {sku}")

                # Insertar en base de datos
                cursor.execute("""
                    INSERT INTO dbo.Producto (FechaCreacion, UsuarioCreacion, Estado, Nombre, SKU, Fuente, Precio)
                    VALUES (GETDATE(), 'scraper', 1, ?, ?, 'Walmart', ?)
                """, nombre.strip(), sku.strip(), precio)
                conn.commit()

            except Exception as e:
                print("⚠️ Error con producto:", e)

        await browser.close()
        cursor.close()
        conn.close()
        print("✅ Proceso completado y productos insertados en SQL Server")

asyncio.run(main())
