import json
from playwright.sync_api import sync_playwright
from loguru import logger

def extraer_categorias_desktop():
    categorias = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        page.goto("https://www.walmart.co.cr/", timeout=60000)

        # Extraer todos los enlaces visibles en modo escritorio
        page.wait_for_selector("a[href^='/']", timeout=10000)
        enlaces = page.query_selector_all("a[href^='/']")

        for enlace in enlaces:
            href = enlace.get_attribute("href")
            if href and href.count("/") >= 1 and not any(x in href for x in ["#", "javascript"]):
                href = href.strip("/")
                if href not in categorias:
                    categorias.append(href)

        browser.close()

    categorias = sorted(set(categorias))
    with open("categorias_walmart_completas.json", "w", encoding="utf-8") as f:
        json.dump(categorias, f, indent=2, ensure_ascii=False)

    logger.success(f"✅ Extraídas {len(categorias)} categorías (modo escritorio)")
    logger.info("📄 Guardado como: categorias_walmart_completas.json")

if __name__ == "__main__":
    extraer_categorias_desktop()
