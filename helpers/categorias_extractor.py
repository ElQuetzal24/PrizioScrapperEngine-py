import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://tienda.pequenomundo.com/"

async def run():
    rutas = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=100)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_timeout(3000)

        # Extraer TODAS las rutas de nivel 0
        nivel0_links = await page.query_selector_all("li.level0 > a")
        for link in nivel0_links:
            href = await link.get_attribute("href")
            if href and href.startswith("https://tienda.pequenomundo.com/"):
                ruta = "/" + "/".join(href.split("/")[3:]).replace(".html", "").strip("/")
                rutas.add(ruta)

        # Hover para mostrar subcategorías
        for link in nivel0_links:
            try:
                await link.hover()
                await page.wait_for_timeout(700)

                sub_links = await page.query_selector_all("li.level1 > a")
                for sublink in sub_links:
                    href = await sublink.get_attribute("href")
                    if href and href.startswith("https://tienda.pequenomundo.com/"):
                        ruta = "/" + "/".join(href.split("/")[3:]).replace(".html", "").strip("/")
                        rutas.add(ruta)
            except:
                continue

        # Guardar en JSON
        rutas_ordenadas = sorted(rutas)
        with open("categorias_pqm.json", "w", encoding="utf-8") as f:
            json.dump(rutas_ordenadas, f, ensure_ascii=False, indent=2)

        print(f"\n {len(rutas_ordenadas)} rutas exportadas a categorias_pqm.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
