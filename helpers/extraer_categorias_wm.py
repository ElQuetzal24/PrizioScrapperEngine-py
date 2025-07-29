from playwright.sync_api import sync_playwright
import time

def abrir_y_recorrer_menu_walmart():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.walmart.co.cr/", timeout=60000)

        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        try:
            contenedor = page.locator("div.walmartcr-mega-menu-1-x-openIconContainer")
            contenedor.wait_for(timeout=10000)
            contenedor.click()
            print("✅ Menú abierto exitosamente.")
        except Exception as e:
            print("❌ Error al hacer clic en el contenedor del menú:", e)
            browser.close()
            return

        time.sleep(2)

        # Hover sobre cada categoría del primer nivel
        categorias = page.locator("ul.walmartcr-mega-menu-1-x-menuColumn ul > li")
        count = categorias.count()
        print(f"🔍 Se encontraron {count} categorías de primer nivel.")

        for i in range(count):
            cat = categorias.nth(i)
            nombre = cat.inner_text().split('\n')[0].strip()
            print(f"🟦 Hover sobre categoría: {nombre}")
            cat.hover()
            time.sleep(1)

            # Subcategorías visibles dentro de la categoría
            subcats = page.locator("ul.walmartcr-mega-menu-1-x-subMenuColumn ul > li")
            subcount = subcats.count()
            for j in range(subcount):
                sub = subcats.nth(j)
                try:
                    subnombre = sub.inner_text().strip()
                    if subnombre:
                        print(f"    └── {subnombre}")
                except:
                    continue

        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    abrir_y_recorrer_menu_walmart()
