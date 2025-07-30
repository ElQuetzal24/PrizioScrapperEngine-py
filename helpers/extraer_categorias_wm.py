
from playwright.sync_api import sync_playwright
import time

def extraer_categorias():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome", slow_mo=60)
        page = browser.new_page()
        page.goto("https://www.walmart.co.cr/", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        # Abrir menú lateral
        page.locator("div.walmartcr-mega-menu-1-x-openIconContainer").click()
        page.wait_for_selector("a.walmartcr-mega-menu-1-x-link", timeout=10000)
        time.sleep(2)

        links = page.locator("a.walmartcr-mega-menu-1-x-link")
        total_links = links.count()
        print(f"\n🧭 Total categorías nivel 1: {total_links}")

        rutas = set()

        for i in range(total_links):
            cat = links.nth(i)
            nombre = cat.inner_text().strip()
            print(f"\n🟨 Procesando: {nombre}")

            # Hover suave + trayecto realista
            box = cat.bounding_box()
            if box:
                x = box["x"] + box["width"] / 2
                y = box["y"] + box["height"] / 2
                page.mouse.move(x, y)
                time.sleep(0.4)
                for offset in range(0, 300, 30):
                    page.mouse.move(x + offset, y)
                    time.sleep(0.05)

            time.sleep(1.2)  # esperar render del childrenContainer

            # Buscar subcategorías con childrenContainer si está visible
            submenu = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer:visible")
            if submenu.count() > 0:
                enlaces = submenu.locator("a:visible")
                print(f"   🧩 Submenú activo con {enlaces.count()} enlaces")
            else:
                enlaces = page.locator("div[role='menu'] a:visible")
                print(f"   🔍 Fallback: {enlaces.count()} enlaces visibles")

            for j in range(enlaces.count()):
                enlace = enlaces.nth(j)
                texto = enlace.inner_text().strip()
                href = enlace.get_attribute("href")
                if texto and href and not href.startswith("https://www.walmart.com"):
                    ruta = f"{nombre} / {texto} | {href}"
                    if ruta not in rutas:
                        rutas.add(ruta)
                        print(f"   🟩 {ruta}")

        # Guardar
        with open("categorias_completas.txt", "w", encoding="utf-8") as f:
            for r in sorted(rutas):
                f.write(r + "\n")

        browser.close()

if __name__ == "__main__":
    extraer_categorias()
