from playwright.sync_api import sync_playwright
import time

def abrir_menu(page):
    page.goto("https://www.walmart.co.cr/", timeout=60000)
    page.wait_for_load_state("domcontentloaded")
    time.sleep(2)
    page.locator("div.walmartcr-mega-menu-1-x-openIconContainer").click()
    page.wait_for_selector("a.walmartcr-mega-menu-1-x-link", timeout=10000)
    return True

def extraer_categorias(page):
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

        box = cat.bounding_box()
        if not box:
            continue

        x = box['x'] + box['width'] / 2
        y = box['y'] + box['height'] / 2

        print(f"\n🟦 {nombre_cat}")

        # 🟡 Hover sobre la categoría
        page.mouse.move(x, y)
        time.sleep(0.6)

        # 🔴 Movimiento lateral como un humano al panel
        page.mouse.move(x + 300, y, steps=30)
        time.sleep(1.2)

        try:
            panel = page.locator("ul.walmartcr-mega-menu-1-x-menu").first
            links = panel.locator("a.walmartcr-mega-menu-1-x-link")
            for j in range(links.count()):
                subcat = links.nth(j).inner_text().strip()
                if subcat and subcat != nombre_cat:
                    print(f"   └── {nombre_cat}/{subcat}")
                    resultados.append(f"{nombre_cat}/{subcat}")
        except Exception as e:
            print(f"⚠️ Panel no visible para {nombre_cat}: {e}")

        time.sleep(0.4)

    with open("categorias_walmart_completo.txt", "w", encoding="utf-8") as f:
        for r in resultados:
            f.write(r + "\n")

    print("\n✅ Exportado a 'categorias_walmart_completo.txt'")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        if abrir_menu(page):
            extraer_categorias(page)
        browser.close()
