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
            nivel1 = cat.inner_text().strip()
            print(f"\n🟨 Procesando: {nivel1}")

            box = cat.bounding_box()
            if box:
                x = box["x"] + box["width"] / 2
                y = box["y"] + box["height"] / 2
                page.mouse.move(x, y)
                time.sleep(0.4)
                for offset in range(0, 300, 30):
                    page.mouse.move(x + offset, y)
                    time.sleep(0.05)

            time.sleep(1.5)

            # Primer submenú (nivel 2)
            children_container = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer:visible")
            if children_container.count() == 0:
                # No hay subcategorías, guardar solo nivel 1
                href = cat.get_attribute("href")
                if href:
                    rutas.add((nivel1, "", "", href))
                    print(f"   🟩 {nivel1} | {href}")
                continue

            subcats = children_container.locator("a.walmartcr-mega-menu-1-x-link:visible")
            for j in range(subcats.count()):
                subcat = subcats.nth(j)
                nivel2 = subcat.inner_text().strip()
                href2 = subcat.get_attribute("href")

                # Hover para descubrir nivel 3
                box2 = subcat.bounding_box()
                if box2:
                    x2 = box2["x"] + box2["width"] / 2
                    y2 = box2["y"] + box2["height"] / 2
                    page.mouse.move(x2, y2)
                    time.sleep(0.3)
                    for offset in range(0, 250, 30):
                        page.mouse.move(x2 + offset, y2)
                        time.sleep(0.05)

                time.sleep(1.2)

                subsub = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer:visible").nth(1)
                if subsub and subsub.locator("a:visible").count() > 0:
                    for k in range(subsub.locator("a:visible").count()):
                        item3 = subsub.locator("a:visible").nth(k)
                        nivel3 = item3.inner_text().strip()
                        href3 = item3.get_attribute("href")
                        if nivel3 and href3:
                            rutas.add((nivel1, nivel2, nivel3, href3))
                            print(f"      🟦 {nivel1} / {nivel2} / {nivel3} | {href3}")
                else:
                    # Solo llega hasta nivel 2
                    if nivel2 and href2:
                        rutas.add((nivel1, nivel2, "", href2))
                        print(f"   🟨 {nivel1} / {nivel2} | {href2}")

        # Guardar en archivo estructurado
        with open("categorias_completas.csv", "w", encoding="utf-8") as f:
            f.write("Nivel1,Nivel2,Nivel3,Href\n")
            for n1, n2, n3, href in sorted(rutas):
                f.write(f"\"{n1}\",\"{n2}\",\"{n3}\",\"{href}\"\n")

        browser.close()

if __name__ == "__main__":
    extraer_categorias()
