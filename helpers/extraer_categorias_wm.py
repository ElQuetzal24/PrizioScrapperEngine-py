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

            # Hover suave
            box = cat.bounding_box()
            if box:
                x = box["x"] + box["width"] / 2
                y = box["y"] + box["height"] / 2
                page.mouse.move(x, y)
                time.sleep(0.4)
                for offset in range(0, 300, 30):
                    page.mouse.move(x + offset, y)
                    time.sleep(0.05)

            time.sleep(1.2)

            submenu = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer:visible")
            if submenu.count() > 0:
                enlaces = submenu.locator("a:visible")
                print(f"   🧩 Submenú activo con {enlaces.count()} enlaces")
            else:
                enlaces = page.locator("div[role='menu'] a:visible")
                print(f"   🔍 Fallback: {enlaces.count()} enlaces visibles")

            for j in range(enlaces.count()):
                enlace = enlaces.nth(j)
                texto_2 = enlace.inner_text().strip()
                href_2 = enlace.get_attribute("href")

                # Hover sobre subcategoría
                box2 = enlace.bounding_box()
                if box2:
                    x2 = box2["x"] + box2["width"] / 2
                    y2 = box2["y"] + box2["height"] / 2
                    page.mouse.move(x2, y2)
                    time.sleep(0.3)
                    for offset in range(0, 250, 30):
                        page.mouse.move(x2 + offset, y2)
                        time.sleep(0.05)

                time.sleep(1)

                # Buscar nivel 3
                subsubmenu = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer:visible").nth(1)
                if subsubmenu and subsubmenu.locator("a:visible").count() > 0:
                    for k in range(subsubmenu.locator("a:visible").count()):
                        enlace_3 = subsubmenu.locator("a:visible").nth(k)
                        texto_3 = enlace_3.inner_text().strip()
                        href_3 = enlace_3.get_attribute("href")
                        if texto_3 and href_3:
                            ruta = f"{nombre} / {texto_2} / {texto_3} | {href_3}"
                            if ruta not in rutas:
                                rutas.add(ruta)
                                print(f"      🟦 {ruta}")
                else:
                    if texto_2 and href_2:
                        ruta = f"{nombre} / {texto_2} | {href_2}"
                        if ruta not in rutas:
                            rutas.add(ruta)
                            print(f"   🟩 {ruta}")

        # Guardar resultados
        with open("categorias_completas.txt", "w", encoding="utf-8") as f:
            for r in sorted(rutas):
                f.write(r + "\n")

        browser.close()

if __name__ == "__main__":
    extraer_categorias()
