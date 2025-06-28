import asyncio
from playwright.async_api import async_playwright

async def obtener_categorias():
    categorias = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.walmart.co.cr/", timeout=60000)

        # Hacer clic en el botón de menú hamburguesa
        try:
            await page.click("button[id='burger-menu']")  # Ajuste si no encuentra ese ID exacto
            await page.wait_for_timeout(2000)  # tiempo para que cargue el menú
        except:
            print("⚠️ No se pudo abrir el menú lateral.")

        # Capturar todos los enlaces visibles después de abrir el menú
        enlaces = await page.query_selector_all("a[href]")

        for enlace in enlaces:
            if not enlace:
                continue

            try:
                href = await enlace.get_attribute("href")
            except:
                continue

            if not href:
                continue

            # Filtrar rutas que parezcan categorías principales
            if (
                href.startswith("/") and
                not any(x in href for x in ["#", "login", "carrito", "search", "p", "account", "tienda", "wishlist"])
                and len(href.strip("/").split("/")) <= 2
            ):
                categorias.add(href.strip("/"))

        await browser.close()

    return sorted(categorias)

if __name__ == "__main__":
    categorias = asyncio.run(obtener_categorias())
    print("📁 Categorías encontradas:")
    for c in categorias:
        print(f"- {c}")
