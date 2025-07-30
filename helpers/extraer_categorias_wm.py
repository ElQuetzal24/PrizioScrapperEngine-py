from playwright.sync_api import sync_playwright
import time

def abrir_menu(page):
    page.goto("https://www.walmart.co.cr/", timeout=60000)
    page.wait_for_load_state("domcontentloaded")
    time.sleep(2)
    page.locator("div.walmartcr-mega-menu-1-x-openIconContainer").click()
    page.wait_for_selector("a.walmartcr-mega-menu-1-x-link", timeout=10000)
    return True

def extraer_categorias_nivel_1(page):
    categorias = page.locator("a.walmartcr-mega-menu-1-x-link")
    total = categorias.count()
    print(f"🔍 Detectadas {total} categorías")

    ya_vistos = set()
    resultados = []

    for i in range(total):
        cat = categorias.nth(i)
        nombre_cat = cat.inner_text().strip()
        if not nombre_cat or nombre_cat in ya_vistos:
            continue
        ya_vistos.add(nombre_cat)
        print(f"🟦 {nombre_cat}")
        resultados.append(nombre_cat)

    with open("categorias_nivel_1.txt", "w", encoding="utf-8") as f:
        for r in resultados:
            f.write(r + "\n")

    print("\n✅ Exportado a 'categorias_nivel_1.txt'")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        if abrir_menu(page):
            extraer_categorias_nivel_1(page)
        browser.close()
