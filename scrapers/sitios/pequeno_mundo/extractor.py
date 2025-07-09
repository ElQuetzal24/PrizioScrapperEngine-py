from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re, os, asyncio
from datetime import datetime

from scrapers.sitios.pequeno_mundo.normalizador import obtener_marca_con_renderizado
from helpers.sku_extractor import extraer_sku_desde_url


CATEGORIA_SELECTORES = [
    "/electrodomesticos.html",
    "/hogar.html",
    "/muebles.html",
    "/ferreteria.html",
    "/mascotas.html",
    "/mallas-construccion.html",
    "/mi-negocio-limpio.html"
]

async def procesar_categorias(categorias, driver, queue):
    cambios_detectados = []

    visitados_path = "logs/productos_visitados.txt"
    os.makedirs("logs", exist_ok=True)
    visitados = set()
    if os.path.exists(visitados_path):
        with open(visitados_path, "r", encoding="utf-8") as f:
            visitados = set(line.strip() for line in f if line.strip())

    errores_log = open("logs/error_scraping.log", "a", encoding="utf-8")
    productos_visitados_log = open(visitados_path, "a", encoding="utf-8")

    for categoria_url in categorias:
        categoria = categoria_url.replace(".html", "").replace("-", " ").capitalize()
        pagina = 1
        while True:
            nuevos = 0
            url = f"https://tienda.pequenomundo.com/{categoria_url}?p={pagina}"
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.product-item'))
                )
            except:
                print(f"No se encontraron productos en {url}")
                break

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            productos = soup.select('li.product-item')
            if not productos:
                break

            for producto in productos:
                try:
                    nombre_el = producto.select_one('.product-item-name')
                    precio_el = producto.select_one('.price')
                    img_el = producto.find('img')
                    enlace_el = producto.select_one('a.product-item-link')

                    nombre = nombre_el.get_text(strip=True) if nombre_el else "N/A"
                    precio = precio_el.get_text(strip=True) if precio_el else "0"
                    imagen = img_el.get('data-src') or img_el.get('src') or ""
                    enlace = enlace_el['href'] if enlace_el and enlace_el.has_attr('href') else "N/A"

                    if not enlace.startswith("http") or enlace in visitados:
                        continue
                    visitados.add(enlace)
                    productos_visitados_log.write(enlace + "\n")
                    nuevos += 1

                    if "pixel.jpg" in imagen or not imagen:
                        imagen = "N/A"

                    precio_valor = float(precio.replace("₡", "").replace(".", "").replace(",", ".").strip())

                    driver.get(enlace)
                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body')))
                    detalle_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # Imagen real desde detalle
                    img_detalle = detalle_soup.select_one('img.fotorama__img')
                    imagen_detalle = (
                        img_detalle.get('data-src')
                        or img_detalle.get('src')
                        or ""
                    ).strip()
                    if imagen_detalle.startswith("https://tienda.pequenomundo.com/media/catalog/product/"):
                        imagen = imagen_detalle
                    sku = await extraer_sku_desde_url(enlace)

                    marca = obtener_marca_con_renderizado(driver, enlace)
                    modelo = re.sub(re.escape(marca), "", nombre, flags=re.IGNORECASE).strip() if marca else nombre

                    print(f"🔍 {nombre} | ₡{precio_valor} | SKU: {sku} | Marca: {marca} | Img: {imagen}")

                    await queue.put((nombre, imagen, sku or "", marca or "", modelo, enlace, categoria, precio_valor, "PequenoMundo"))
                    cambios_detectados.append([nombre, precio_valor, marca, categoria, enlace, imagen])

                except Exception as e:
                    errores_log.write(f"{datetime.now()} | Error en {enlace}: {e}\n")
                    print(f"Error procesando producto: {e}")
                    continue

            print(f" Página {pagina} de {categoria} procesada.")
            if nuevos == 0:
                break
            pagina += 1

    productos_visitados_log.close()
    errores_log.close()
    return cambios_detectados
