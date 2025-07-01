import asyncio
from playwright.async_api import async_playwright

URL = "https://tienda.pequenomundo.com/hogar/fiesta.html?product_list_limit=all"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="es-CR"
        )

        page = await context.new_page()
        await page.goto(URL, timeout=60000)

        # Scroll profundo para disparar renderizado
        for _ in range(5):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(1000)

        try:
            await page.wait_for_selector("li.product-item", timeout=30000)
        except:
            print("❌ No se encontraron productos después de esperar.")
            await browser.close()
            return

        productos = await page.query_selector_all("li.product-item")
        print(f"\n✅ Total productos encontrados: {len(productos)}\n")

        for producto in productos:
            nombre_el = await producto.query_selector("a.product-item-link")
            precio_el = await producto.query_selector("span.price")
            nombre = (await nombre_el.text_content()).strip() if nombre_el else "N/A"
            precio = (await precio_el.text_content()).strip() if precio_el else "N/A"
            url = await nombre_el.get_attribute("href") if nombre_el else "N/A"
            print(f"🛍️ {nombre} | {precio} | {url}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
