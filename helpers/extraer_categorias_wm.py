from playwright.sync_api import sync_playwright
import time

def abrir_menu_walmart():
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

        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    abrir_menu_walmart()
