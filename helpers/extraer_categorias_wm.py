from playwright.sync_api import sync_playwright
import time

def extraer_tres_niveles():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.walmart.co.cr/", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

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

        categorias = page.locator("a.walmartcr-mega-menu-1-x-link")
        count = categorias.count()
        print(f"🔍 {count} categorías principales encontradas.")

        for i in range(count):
            categoria = categorias.nth(i)
            try:
                nombre = categoria.inner_text().strip()
                if not nombre:
                    continue
                print(f"🟦 {nombre}")
                resultados.append(nombre)
                categoria.hover()
                time.sleep(1.2)

                # Subcategorías visibles
                subcategorias = page.locator("ul.walmartcr-mega-menu-1-x-subMenuColumn li")
                subcount = subcategorias.count()
                for j in range(subcount):
                    subcat = subcategorias.nth(j)
                    try:
                        nombre_sub = subcat.inner_text().strip()
                        if not nombre_sub:
                            continue
                        print(f"    └── {nombre_sub}")
                        resultados.append(f"    └── {nombre_sub}")
                        subcat.hover()
                        time.sleep(1)

                        # Sub-subcategorías visibles dentro de columna a la derecha
                        subsub = page.locator("ul.walmartcr-mega-menu-1-x-menu > li > span")
                        subsubcount = subsub.count()
                        for k in range(subsubcount):
                            item = subsub.nth(k)
                            nombre_subsub = item.inner_text().strip()
                            if nombre_subsub:
                                print(f"        └── {nombre_subsub}")
                                resultados.append(f"        └── {nombre_subsub}")
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Error en categoría {i}: {e}")
                continue

        with open("categorias_walmart_3niveles.txt", "w", encoding="utf-8") as f:
            for linea in resultados:
                f.write(linea + "\n")

        print("✅ Exportado a 'categorias_walmart_3niveles.txt'")
        browser.close()

if __name__ == "__main__":
    extraer_tres_niveles()
