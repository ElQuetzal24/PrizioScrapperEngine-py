from playwright.async_api import async_playwright
from logger import logger  # Asegúrate de tener logger.py correctamente importado

async def lanzar_navegador():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    return browser

async def scroll_hasta_cargar_todos(page):
    productos_previos = -1
    ciclos_sin_cambio = 0
    max_sin_cambio = 2
    max_ciclos = 2  # máximo de intentos para evitar bucles infinitos
    velocidad_scroll = 200  # milisegundos entre ciclos

    for ciclo in range(max_ciclos):
        try:
            await page.keyboard.press("End")
            await page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
            await page.wait_for_timeout(velocidad_scroll)

            productos_actuales = await page.locator(".vtex-search-result-3-x-galleryItem").count()
            logger.info(f"Scroll {ciclo+1}: {productos_actuales} productos visibles")

            if productos_actuales == productos_previos:
                ciclos_sin_cambio += 1
            else:
                ciclos_sin_cambio = 0
                productos_previos = productos_actuales

            if ciclos_sin_cambio >= max_sin_cambio:
                logger.info(f"Scroll finalizado: {productos_actuales} productos cargados (sin cambios en {max_sin_cambio} ciclos)")
                break
        except Exception as e:
            logger.error(f" Error durante scroll: {e}")
            break

    else:
        logger.info(f"Fin de scroll por límite de ciclos ({max_ciclos}). Productos detectados: {productos_actuales}")

async def safe_text_content(element):
    try:
        if element:
            return await element.text_content()
        return None
    except Exception as e:
        logger.warning(f"safe_text_content falló: {e}")
        return None
