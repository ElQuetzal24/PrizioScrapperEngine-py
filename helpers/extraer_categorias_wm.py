import json
from playwright.sync_api import sync_playwright
from loguru import logger
import time

def extraer_categorias_navegando_menu():
    rutas = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        page.goto("https://www.walmart.co.cr/", timeout=60000)

        # Esperar que cargue el menú horizontal
        page.wait_for_selector("nav", timeout=10000)
        items_menu = page.query_selector_all("nav li a[href^='/']")

        logger.info(f"🧭 Explorando {len(items_menu)} categorías principales...")

        for item in items_menu:
            try:
                item.hover()
                time.sleep(0.7)  # dejar que aparezcan subniveles
            except:
                continue

            enlaces = page.query_selector_all("a[href^='/']")
            for enlace in enlaces:
                href = enlace.get_attribute("href")
                if not href or "?" in href or "#" in href or "javascript" in href:
                    continue
                ruta = href.strip("/")
                if ruta and not ruta.startswith("?") and not ruta.startswith("#"):
                    rutas.add(ruta)

        browser.close()

    rutas_limpias = sorted(rutas)
    with open("categorias_walmart_completas.json", "w", encoding="utf-8") as f:
        json.dump(rutas_limpias, f, indent=2, ensure_ascii=False)

    logger.success(f"✅ Extraídas {len(rutas_limpias)} rutas desde el menú superior.")
    logger.info("📄 Guardado en: categorias_walmart_completas.json")

if __name__ == "__main__":
    extraer_categorias_navegando_menu()
