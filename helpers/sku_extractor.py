import asyncio
from playwright.async_api import async_playwright
import re

async def extraer_sku_desde_url(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_timeout(3000)

            texto = await page.text_content('body')
            match = re.search(r"SKU\s*[:\s]*([0-9]{6,})", texto, re.IGNORECASE)

            await browser.close()
            return match.group(1) if match else "SKUGENERICO"
    except Exception as e:
        print(f"❌ Error con Playwright al extraer SKU de {url}: {e}")
        return "SKUGENERICO"
