from playwright.sync_api import sync_playwright
import time
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Ajustá si está en otra ruta

def abrir_menu(page):
    page.goto("https://www.walmart.co.cr/", timeout=60000)
    page.wait_for_load_state("domcontentloaded")
    time.sleep(2)
    page.locator("div.walmartcr-mega-menu-1-x-openIconContainer").click()
    page.wait_for_selector("a.walmartcr-mega-menu-1-x-link", timeout=10000)
    return True
def extraer_rutas(page):
    rutas = set()

    categorias_lvl1 = page.locator("a.walmartcr-mega-menu-1-x-link")
    total = categorias_lvl1.count()

    for i in range(total):
        try:
            cat1 = categorias_lvl1.nth(i)
            nombre1 = cat1.inner_text().strip()
            if not nombre1:
                continue

            print(f"\n🟨 Procesando: {nombre1}")

            # Simular hover real y esperar que se abra el panel lateral
            box = cat1.bounding_box()
            if not box:
                continue
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            page.mouse.move(x, y)
            time.sleep(0.3)
            page.mouse.move(x + 2, y + 2)
            time.sleep(1.2)

            subcats = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer ul li")

            if subcats.count() == 0:
                rutas.add(nombre1)
                print(f"🟦 {nombre1}")
                continue

            for j in range(subcats.count()):
                li = subcats.nth(j)
                nombre2 = ""
                href = ""

                if li.locator("a").count() > 0:
                    a = li.locator("a").first
                    nombre2 = a.inner_text().strip()
                    href = a.get_attribute("href")
                    ruta = f"{nombre1}/{nombre2}"
                    rutas.add(ruta)
                    print(f"✅ {ruta}")

                elif li.locator("span").count() > 0:
                    nombre2 = li.locator("span").inner_text().strip()
                    hijos_nivel3 = li.locator("ul li")

                    if hijos_nivel3.count() > 0:
                        for k in range(hijos_nivel3.count()):
                            li3 = hijos_nivel3.nth(k)
                            if li3.locator("a").count() > 0:
                                a3 = li3.locator("a").first
                                nombre3 = a3.inner_text().strip()
                                if nombre3:
                                    ruta = f"{nombre1}/{nombre2}/{nombre3}"
                                    rutas.add(ruta)
                                    print(f"🔷 {ruta}")
                    else:
                        if nombre2:
                            ruta = f"{nombre1}/{nombre2}"
                            rutas.add(ruta)
                            print(f"✅ {ruta}")
        except Exception as e:
            print(f"⚠️ Error en categoría {i}: {e}")
            continue

    return sorted(rutas)

    rutas = set()

    for i in range(30):
        try:
            categorias_lvl1 = page.locator("a.walmartcr-mega-menu-1-x-link")
            if categorias_lvl1.count() <= i:
                break

            cat1 = categorias_lvl1.nth(i)
            nombre1 = cat1.inner_text().strip()
            if not nombre1:
                continue

            print(f"\n🟨 Procesando: {nombre1}")
            box = cat1.bounding_box()
            if not box:
                continue
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            page.mouse.move(x, y)
            time.sleep(0.6)

            subcats = page.locator("div.walmartcr-mega-menu-1-x-childrenContainer ul li")

            if subcats.count() == 0:
                rutas.add(nombre1)
                print(f"🟦 {nombre1}")
                continue

            for j in range(subcats.count()):
                li = subcats.nth(j)
                nombre2 = ""
                href = ""

                if li.locator("a").count() > 0:
                    a = li.locator("a").first
                    nombre2 = a.inner_text().strip()
                    href = a.get_attribute("href")
                    ruta = f"{nombre1}/{nombre2}"
                    rutas.add(ruta)
                    print(f"✅ {ruta}")

                elif li.locator("span").count() > 0:
                    nombre2 = li.locator("span").inner_text().strip()

                    hijos_nivel3 = li.locator("ul li")
                    if hijos_nivel3.count() > 0:
                        for k in range(hijos_nivel3.count()):
                            li3 = hijos_nivel3.nth(k)
                            if li3.locator("a").count() > 0:
                                a3 = li3.locator("a").first
                                nombre3 = a3.inner_text().strip()
                                if nombre3:
                                    ruta = f"{nombre1}/{nombre2}/{nombre3}"
                                    rutas.add(ruta)
                                    print(f"🔷 {ruta}")
                    else:
                        if nombre2:
                            ruta = f"{nombre1}/{nombre2}"
                            rutas.add(ruta)
                            print(f"✅ {ruta}")
        except Exception as e:
            print(f"⚠️ Error en categoría {i}: {e}")
            continue

    return sorted(rutas)

if __name__ == "__main__":
    with sync_playwright() as p:
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            executable_path=CHROME_PATH,
            slow_mo=50,
            args=["--start-maximized"]
        )
        page = context.new_page()

        if abrir_menu(page):
            rutas = extraer_rutas(page)
            with open("categorias_completas.txt", "w", encoding="utf-8") as f:
                for r in rutas:
                    f.write(r + "\n")

        context.close()
