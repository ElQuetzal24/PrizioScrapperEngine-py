from playwright.sync_api import sync_playwright
import time

def abrir_menu(page):
    page.goto("https://www.walmart.co.cr/", timeout=60000)
    page.wait_for_load_state("domcontentloaded")
    time.sleep(2)
    page.locator("div.walmartcr-mega-menu-1-x-openIconContainer").click()
    page.wait_for_selector("a.walmartcr-mega-menu-1-x-link", timeout=10000)
    return True

def extraer_rutas_completas(page):
    rutas = []
    categorias_lvl1 = page.locator("a.walmartcr-mega-menu-1-x-link")
    total = categorias_lvl1.count()

    for i in range(total):
        cat1 = categorias_lvl1.nth(i)
        nombre1 = cat1.inner_text().strip()
        if not nombre1:
            continue

        box = cat1.bounding_box()
        if not box:
            continue
        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2
        page.mouse.move(x, y)
        time.sleep(1.0)

        if nombre1 == "Electrónica":
            print("🧪 DEBUG: Hover sobre Electrónica confirmado")

        containers = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer").all()
        subcats_lvl2 = None
        for cont in containers:
            if cont.bounding_box():
                subcats_lvl2 = cont.locator("ul > li")
                break

        if not subcats_lvl2 or subcats_lvl2.count() == 0:
            print(f"🟦 {nombre1}")
            rutas.append(nombre1)
            continue

        for j in range(subcats_lvl2.count()):
            subcat2 = subcats_lvl2.nth(j)
            nombre2 = subcat2.inner_text().strip()
            if not nombre2:
                continue

            if nombre1 == "Electrónica":
                print(f"🔍 DEBUG: Subcategoría encontrada: {nombre2}")

            box2 = subcat2.bounding_box()
            if not box2:
                continue
            page.mouse.move(box2["x"] + box2["width"]/2, box2["y"] + box2["height"]/2)
            time.sleep(0.5)

            containers_lvl3 = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer").all()
            subcats_lvl3 = None
            for cont3 in containers_lvl3:
                if cont3.bounding_box():
                    subcats_lvl3 = cont3.locator("ul > li")
                    break

            found_lvl3 = False
            if subcats_lvl3 and subcats_lvl3.count() > 0:
                for k in range(subcats_lvl3.count()):
                    subcat3 = subcats_lvl3.nth(k)
                    nombre3 = subcat3.inner_text().strip()
                    if nombre3 and nombre3 not in [nombre1, nombre2]:
                        ruta = f"{nombre1}/{nombre2}/{nombre3}"
                        print(f"✅ {ruta}")
                        rutas.append(ruta)
                        found_lvl3 = True

            if not found_lvl3:
                ruta = f"{nombre1}/{nombre2}"
                print(f"✅ {ruta}")
                rutas.append(ruta)

    return rutas

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        if abrir_menu(page):
            rutas = extraer_rutas_completas(page)
            with open("categorias_debug.txt", "w", encoding="utf-8") as f:
                for r in rutas:
                    f.write(r + "\n")
        browser.close()
