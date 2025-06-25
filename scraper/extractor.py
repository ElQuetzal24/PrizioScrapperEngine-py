from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import os
from datetime import datetime
import csv

from scraper.normalizador import obtener_marca_con_renderizado, obtener_sku_renderizado
from repositorio.sql_server import insertar_o_actualizar_producto

CATEGORIA_SELECTORES = [
    "/electrodomesticos.html",
    "/hogar.html"
]

def procesar_categorias(driver):
    cambios_detectados = []

    # === Cargar productos ya visitados de ejecuciones previas ===
    visitados_path = "logs/productos_visitados.txt"
    os.makedirs("logs", exist_ok=True)  # Asegura que la carpeta exista

    visitados = set()
    if os.path.exists(visitados_path):
        with open(visitados_path, "r", encoding="utf-8") as f:
            visitados = set(line.strip() for line in f if line.strip())

    # Archivos abiertos 1 sola vez
    errores_log = open("logs/error_scraping.log", "a", encoding="utf-8")
    productos_visitados_log = open(visitados_path, "a", encoding="utf-8")

    for categoria_url in CATEGORIA_SELECTORES:
        categoria = categoria_url.replace(".html", "").replace("-", " ").capitalize()
        pagina = 1
        while True:
            nuevos = 0
            url = f"https://tienda.pequenomundo.com/{categoria_url}?p={pagina}"
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.product-item'))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            productos = soup.select('li.product-item')

            if not productos:
                break

            for producto in productos:
                try:
                    enlace_el = producto.select_one('a.product-item-link')
                    enlace = enlace_el['href'] if enlace_el and enlace_el.has_attr('href') else "N/A"

                    if enlace in visitados or not enlace.startswith("http"):
                        continue
                    visitados.add(enlace)
                    productos_visitados_log.write(enlace + "\n")
                    nuevos += 1

                    # Ir al detalle del producto
                    driver.get(enlace)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body'))
                    )
                    detalle_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    nombre_el = producto.select_one('.product-item-name')
                    precio_el = producto.select_one('.price')
                    nombre = nombre_el.get_text(strip=True) if nombre_el else "N/A"
                    precio = precio_el.get_text(strip=True) if precio_el else "0"

                    # Imagen del detalle
                    img_detalle = detalle_soup.select_one('img.fotorama__img')
                    imagen = img_detalle.get('src') if img_detalle and img_detalle.has_attr('src') else "N/A"
                    if not imagen.startswith("https://tienda.pequenomundo.com/media/catalog"):
                        imagen = "N/A"

                    precio_valor = float(precio.replace("₡", "").replace(".", "").replace(",", ".").strip())

                    sku = obtener_sku_renderizado(driver)
                    marca = obtener_marca_con_renderizado(driver, enlace)
                    modelo = re.sub(re.escape(marca), "", nombre, flags=re.IGNORECASE).strip()

                    fue_insertado = insertar_o_actualizar_producto(
                        nombre, imagen, sku, marca, modelo, enlace, categoria, precio_valor
                    )
                    if fue_insertado:
                        cambios_detectados.append([nombre, precio_valor, marca, categoria, enlace, imagen])

                except Exception as e:
                    errores_log.write(f"{datetime.now()} | Error en {enlace}: {e}\n")
                    print(f"❌ Error procesando producto: {e}")
                    continue

            print(f"✅ Página {pagina} de categoría {categoria} procesada.")
            if nuevos == 0:
                break
            pagina += 1

    productos_visitados_log.close()
    errores_log.close()
    return cambios_detectados
