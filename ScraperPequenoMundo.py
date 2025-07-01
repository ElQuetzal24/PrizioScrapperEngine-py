import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://tienda.pequenomundo.com/hogar/fiesta.html"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(BASE_URL, timeout=60000)

        # Scroll para forzar renderizado y esperar carga
        await page.wait_for_timeout(2000)
        await page.mouse.wheel(0, 3000)

        # Esperar que desaparezca el loader
        try:
            await page.wait_for_selector(".loading-mask", timeout=15000, state="hidden")
        except:
            print("⚠️ No se detectó loader (probablemente ya desapareció).")

        # Esperar que aparezcan los productos
        await page.wait_for_selector("li.product-item", timeout=20000)

        # Detectar total de páginas
        paginas = await page.query_selector_all("ul.items.pages-items li.item a.page")
        total_paginas = max([int(await el.text_content()) for el in paginas]) if paginas else 1
        print(f"📄 Total páginas detectadas: {total_paginas}")

        total_encontrados = 0
        historial_hashes = set()

        for page_num in range(1, total_paginas + 1):
            url = f"{BASE_URL}?p={page_num}"
            await page.goto(url, timeout=60000)

            try:
                await page.wait_for_selector(".loading-mask", timeout=10000, state="hidden")
            except:
                pass

            await page.wait_for_timeout(2000)
            await page.mouse.wheel(0, 3000)

            try:
                await page.wait_for_selector("li.product-item", timeout=20000, state="visible")
            except:
                print(f"⚠️ No hay productos visibles en página {page_num}")
                break

            productos = await page.query_selector_all("li.product-item")
            if not productos:
                print(f"🚫 Fin del catálogo en página {page_num}")
                break

            print(f"\n📄 Página {page_num} - {len(productos)} productos encontrados:")

            # Evitar repetición infinita
            hash_pagina = "|".join([
                await (await p.query_selector("a.product-item-link")).get_attribute("href") or "N/A"
                for p in productos
            ])
            if hash_pagina in historial_hashes:
                print(f"⚠️ Página repetida detectada. Deteniendo scraping.")
                break
            historial_hashes.add(hash_pagina)

            for producto in productos:
                nombre_el = await producto.query_selector("a.product-item-link")
                precio_el = await producto.query_selector("span.price")

                nombre = (await nombre_el.text_content()).strip() if nombre_el else "N/A"
                precio = (await precio_el.text_content()).strip() if precio_el else "N/A"
                url_prod = await nombre_el.get_attribute("href") if nombre_el else "N/A"

                print(f"🛍️ {nombre} | {precio} | {url_prod}")
                total_encontrados += 1

        print(f"\n✅ Total productos únicos encontrados: {total_encontrados}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
