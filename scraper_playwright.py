import asyncio
import csv
from playwright.async_api import async_playwright
import re

OUTPUT_FILE = "productos.csv"
CATEGORIA_URL = "https://www.walmart.co.cr/articulos-para-el-hogar"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        await page.goto(CATEGORIA_URL, timeout=30000)

        # Scroll repetido para forzar carga dinámica
        for _ in range(10):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(1000)

        await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=15000)

        productos = await page.locator(".vtex-search-result-3-x-galleryItem").element_handles()

        resultados = []

      #  for p_item in productos [:10000]:  # puedes quitar el [:10] para todos
        for p_item in productos:
            try:
                nombre_el = await p_item.query_selector(".vtex-product-summary-2-x-productBrand")
                nombre = await nombre_el.inner_text() if nombre_el else "N/A"

                link_el = await p_item.query_selector("a")
                href = await link_el.get_attribute("href") if link_el else None

                if not href:
                    continue

                url = f"https://www.walmart.co.cr{href}" if href.startswith("/") else href

                # Ir a la página del producto
                product_page = await context.new_page()
                await product_page.goto(url, timeout=30000)
                await product_page.wait_for_timeout(2000)

                # PRECIO
                try:
                    price_el = await product_page.query_selector(".vtex-store-components-3-x-price_sellingPrice span")
                    raw_price = await price_el.inner_text() if price_el else "0"
                    price_clean = raw_price.replace("₡", "").replace(".", "").replace(",", "").strip()
                    precio = float(price_clean)
                except:
                    precio = 0.0

                # SKU
                try:
                    await product_page.wait_for_selector(".vtex-store-components-3-x-productReference", timeout=5000)
                    try:
     
                        #aca
                        html = await product_page.content()
        
                            # Extraer el texto justo antes del título principal del producto
                            # Este patrón busca un número largo justo antes de <h1>
                        match = re.search(r">(\d{11,14})</span>\s*<h1", html)
        
                        if match:
                            sku = match.group(1)
                        else:
                            # fallback: busca cualquier número largo aislado
                            posibles = re.findall(r">\s*(\d{11,14})\s*<", html)
                            sku = posibles[0] if posibles else "N/A"
                    #aca
                    except:
                        sku = "N/A"

                except:
                    sku = "N/A"

                await product_page.close()

                print(f"✔ {nombre} | ₡{precio:,.0f} | SKU: {sku}")

                resultados.append({
                    "nombre": nombre.strip(),
                    "precio": precio,
                    "sku": sku.strip(),
                    "url": url.strip()
                })

            except Exception as e:
                print("⚠️ Error con producto:", e)

        # Guardar CSV
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["nombre", "precio", "sku", "url"])
            writer.writeheader()
            for row in resultados:
                writer.writerow(row)

        print(f"\n✅ {len(resultados)} productos guardados en {OUTPUT_FILE}")
        await browser.close()

asyncio.run(main())
