import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://tienda.pequenomundo.com/hogar/fiesta.html"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        page_num = 1
        total_encontrados = 0

        while True:
            url = f"{BASE_URL}?p={page_num}"
            await page.goto(url, timeout=60000)

            try:
                await page.wait_for_selector(".loading-mask", timeout=15000, state="hidden")
            except:
                pass  # por si no aparece

            try:
                await page.wait_for_selector("li.product-item", timeout=10000, state="visible")
            except:
                print(f"❌ No hay más productos en página {page_num}")
                break  # Terminamos el bucle si ya no hay productos

            productos = await page.query_selector_all("li.product-item")

            if not productos:
                print(f"⚠️ Página {page_num} vacía")
                break

            print(f"\n📄 Página {page_num} - {len(productos)} productos encontrados:\n")
            total_encontrados += len(productos)

            for producto in productos:
                nombre_el = await producto.query_selector("a.product-item-link")
                precio_el = await producto.query_selector("span.price")

                nombre = (await nombre_el.text_content()).strip() if nombre_el else "N/A"
                precio = (await precio_el.text_content()).strip() if precio_el else "N/A"
                url_prod = await nombre_el.get_attribute("href") if nombre_el else "N/A"

                print(f"🛍️ {nombre} | {precio} | https://tienda.pequenomundo.com{url_prod}")

            page_num += 1

        print(f"\n✅ Total productos encontrados: {total_encontrados}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
