from playwright.sync_api import sync_playwright
import time

def extraer_menu_corregido():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.walmart.co.cr/", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        # Abrir menú lateral
        try:
            menu_button = page.locator("div.walmartcr-mega-menu-1-x-openIconContainer")
            menu_button.wait_for(timeout=10000)
            menu_button.click()
            print("✅ Menú abierto")
        except Exception as e:
            print("❌ Error al abrir menú:", e)
            browser.close()
            return

        time.sleep(2)

        resultados = []

        # Seleccionar todos los elementos de categorías visibles del primer nivel
        categorias = page.locator("a.walmartcr-mega-menu-1-x-link")
        count = categorias.count()
        print(f"🔍 {count} categorías principales encontradas.")

        for i in range(count):
            categoria = categorias.nth(i)
            try:
                nombre = categoria.inner_text().strip()
                if not nombre:
                    continue

                print(f"🟦 Categoría: {nombre}")
                resultados.append(nombre)
                categoria.hover()
                time.sleep(1.5)

                # Buscar subcategorías si aparecen
                subcategorias = page.locator("ul.walmartcr-mega-menu-1-x-subMenuColumn li")
                for j in range(subcategorias.count()):
                    subcat = subcategorias.nth(j)
                    try:
                        subnombre = subcat.inner_text().strip()
                        if subnombre:
                            print(f"    └── {subnombre}")
                            resultados.append(f"    └── {subnombre}")
                    except:
                        continue

            except Exception as e:
                print(f"⚠️ Error al procesar categoría: {e}")
                continue

        # Guardar en archivo
        with open("categorias_walmart.txt", "w", encoding="utf-8") as f:
            for linea in resultados:
                f.write(linea + "\n")

        print("✅ Menú exportado a 'categorias_walmart.txt'")
        browser.close()

if __name__ == "__main__":
    extraer_menu_corregido()
