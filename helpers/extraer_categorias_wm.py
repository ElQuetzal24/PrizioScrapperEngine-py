from playwright.sync_api import sync_playwright
import time

def extraer_menu_walmart_completo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=70)
        page = browser.new_page()
        page.goto("https://www.walmart.co.cr/", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        try:
            page.locator("div.walmartcr-mega-menu-1-x-openIconContainer").click()
            print("✅ Menú abierto")
        except Exception as e:
            print("❌ No se pudo abrir el menú:", e)
            browser.close()
            return

        time.sleep(2)
        resultados = []

        categorias = page.locator("a.walmartcr-mega-menu-1-x-link")
        total_categorias = categorias.count()
        print(f"🔍 {total_categorias} enlaces de menú detectados")

        for i in range(total_categorias):
            categoria = categorias.nth(i)
            nombre_cat = categoria.inner_text().strip()
            href = categoria.get_attribute("href")

            if not nombre_cat or not href:
                continue

            box_cat = categoria.bounding_box()
            if not box_cat:
                continue

            print(f"🟦 {nombre_cat}")
            resultados.append(nombre_cat)

            # Hover para que despliegue subcategorías
            x_cat = box_cat["x"] + box_cat["width"] / 2
            y_cat = box_cat["y"] + box_cat["height"] / 2
            page.mouse.move(x_cat, y_cat)
            time.sleep(1.3)

            # Obtener columnas de subcategorías (las múltiples UL de nivel 2 visibles)
            columnas_submenu = page.locator("ul.walmartcr-mega-menu-1-x-menu")
            col_count = columnas_submenu.count()

            for j in range(col_count):
                columna = columnas_submenu.nth(j)
                sublinks = columna.locator("a.walmartcr-mega-menu-1-x-link")
                subcount = sublinks.count()

                for k in range(subcount):
                    subcat = sublinks.nth(k)
                    nombre_sub = subcat.inner_text().strip()
                    href_sub = subcat.get_attribute("href")
                    if nombre_sub and href_sub and nombre_sub != nombre_cat:
                        print(f"    └── {nombre_sub}")
                        resultados.append(f"    └── {nombre_sub}")

            time.sleep(1)

        with open("categorias_walmart_completo.txt", "w", encoding="utf-8") as f:
            for r in resultados:
                f.write(r + "\n")

        print("✅ Exportado a 'categorias_walmart_completo.txt'")
        browser.close()

if __name__ == "__main__":
    extraer_menu_walmart_completo()
