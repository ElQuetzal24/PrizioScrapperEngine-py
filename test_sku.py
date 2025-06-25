import asyncio
from playwright.async_api import async_playwright
import re

async def obtener_sku(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        # Esperamos unos segundos a que cargue todo el contenido JS
        await page.wait_for_timeout(3000)

        # Obtener TODO el texto visible de la página
        texto_completo = await page.text_content('body')

        # Buscar el patrón del SKU
        match = re.search(r'SKU\s*[:\s]*([0-9]{6,})', texto_completo, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

if __name__ == "__main__":
    url = "https://tienda.pequenomundo.com/batidora-pedestal-westinghouse.html"
    sku = asyncio.run(obtener_sku(url))
    print("✅ SKU extraído:", sku if sku else "No encontrado")
