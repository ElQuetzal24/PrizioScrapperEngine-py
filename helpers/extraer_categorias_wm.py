import asyncio
from playwright.async_api import async_playwright
import json

async def extract_walmart_menu():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.walmart.co.cr/")

        # Esperar que el menú esté listo
        await page.wait_for_selector("nav")

        menu_data = []

        # Selector del menú principal (nivel 1)
        nivel1_selector = 'nav > ul > li > a'  # Ajusta según el DOM real

        nivel1_elements = await page.query_selector_all(nivel1_selector)
        for i, nivel1 in enumerate(nivel1_elements):
            nivel1_text = await nivel1.inner_text()
            nivel1_href = await nivel1.get_attribute("href")
            
            # Hover para desplegar menú lateral (nivel 2)
            await nivel1.hover()
            await page.wait_for_timeout(1000)  # Espera a que cargue el submenú
            
            # Extraer nivel 2
            nivel2_selector = "div[class*='walmartcr-mega-menu-1-x-childrenContainer'] a"
            nivel2_elements = await page.query_selector_all(nivel2_selector)
            nivel2_data = []
            for nivel2 in nivel2_elements:
                nivel2_text = await nivel2.inner_text()
                nivel2_href = await nivel2.get_attribute("href")
                
                # Hover sobre nivel 2 para mostrar nivel 3 si aplica
                await nivel2.hover()
                await page.wait_for_timeout(500)
                
                # Extraer nivel 3
                nivel3_selector = "div[class*='walmartcr-mega-menu-1-x-childrenContainer'] a"
                nivel3_elements = await page.query_selector_all(nivel3_selector)
                nivel3_data = []
                for nivel3 in nivel3_elements:
                    nivel3_text = await nivel3.inner_text()
                    nivel3_href = await nivel3.get_attribute("href")
                    nivel3_data.append({
                        "text": nivel3_text,
                        "href": nivel3_href
                    })

                nivel2_data.append({
                    "text": nivel2_text,
                    "href": nivel2_href,
                    "children": nivel3_data
                })
            
            menu_data.append({
                "text": nivel1_text,
                "href": nivel1_href,
                "children": nivel2_data
            })

        await browser.close()

        # Guardar resultado JSON
        with open("walmart_menu.json", "w", encoding="utf-8") as f:
            json.dump(menu_data, f, ensure_ascii=False, indent=2)

asyncio.run(extract_walmart_menu())
