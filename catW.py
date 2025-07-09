import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://tienda.pequenomundo.com/"
BASE = "https://tienda.pequenomundo.com"

async def run():
    categorias = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_timeout(2000)

        # Selector general del menú principal
        menu_items = await page.query_selector_all("ul#menu-nav > li.level0")

        for item in menu_items:
            await item.hover()
            await page.wait_for_timeout(800)

            # Buscar todos los enlaces dentro del submenu
            links = await item.query_selector_all("ul.level1 li.level1 a")

            for link in links:
                href = await link.get_attribute("href")
                if href and BASE in href:
                    rel = "/" + "/".join(href.split("/")[3:]).replace(".html", "").strip("/")
                    categorias.append(rel)

        categorias = sorted(set(categorias))
        with open("categorias.json", "w", encoding="utf-8") as f:
            json.dump(categorias, f, ensure_ascii=False, indent=2)

        print(f"\n✅ {len(categorias)} rutas exportadas a categorias.json")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
