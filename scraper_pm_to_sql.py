import pyodbc
import csv
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Conexión BD
conexion = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=scrap_db;"
    "Trusted_Connection=yes;"
)
cursor = conexion.cursor()

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

CATEGORIA_SELECTORES = [
    
    "/mallas-construccion.html", "/mascotas.html",  "/mi-negocio-limpio.html"
]

def obtener_marca_con_renderizado(driver, url_producto):
    try:
        driver.get(url_producto)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for li in soup.find_all("li"):
            texto = li.get_text(separator=" ", strip=True)
            if "marca" in texto.lower():
                partes = texto.split(":")
                if len(partes) > 1:
                    return partes[1].strip()
        return "Marca no encontrada"
    except Exception as e:
        print(f"Error renderizando marca desde {url_producto}: {e}")
        return "Error al renderizar"

def obtener_sku_renderizado(driver):
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posibles = soup.find_all(string=re.compile("SKU", re.IGNORECASE))
        for texto in posibles:
            match = re.search(r"SKU[:\s]*([0-9]+)", texto)
            if match:
                return match.group(1)
        return None
    except Exception as e:
        print(f"Error extrayendo SKU: {e}")
        return None

cambios_detectados = []

for categoria_url in CATEGORIA_SELECTORES:
    visitados = set()
    pagina = 1
    while True:
        nuevos = 0
        url = f"https://tienda.pequenomundo.com/{categoria_url}?p={pagina}"
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.product-item')))
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
                imagen = img_el.get('data-src') or img_el.get('src') or "N/A"
                enlace = enlace_el['href'] if enlace_el and enlace_el.has_attr('href') else "N/A"

                if enlace in visitados:
                    continue
                visitados.add(enlace)
                nuevos += 1

                categoria = categoria_url.replace(".html", "").replace("-", " ").capitalize()
                if imagen.startswith("data:image"):
                    imagen = "N/A"

                precio_valor = float(precio.replace("₡", "").replace(".", "").replace(",", ".").strip())

                driver.get(enlace)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body')))

                sku = obtener_sku_renderizado(driver)
                marca = obtener_marca_con_renderizado(driver, enlace)
                modelo = re.sub(re.escape(marca), "", nombre, flags=re.IGNORECASE).strip()

                cursor.execute("SELECT ProductoId FROM Producto WHERE Nombre = ? AND Fuente = ?", nombre, 'PequenoMundo')
                fila = cursor.fetchone()

                if fila:
                    producto_id = fila[0]
                    cursor.execute("SELECT TOP 1 Precio FROM PrecioProducto WHERE ProductoId = ? ORDER BY FechaRegistro DESC", producto_id)
                    ultimo = cursor.fetchone()
                    if not ultimo or float(ultimo[0]) != precio_valor:
                        cursor.execute("INSERT INTO PrecioProducto (ProductoId, Precio) VALUES (?, ?)", producto_id, precio_valor)
                        conexion.commit()
                        cambios_detectados.append([nombre, precio_valor, marca, categoria, enlace, imagen])
                else:
                    cursor.execute("""
                        INSERT INTO Producto (Nombre, ImagenUrl, Fuente, SKU, Marca, Modelo, UrlCompra, Categoria)
                        OUTPUT INSERTED.ProductoId
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, nombre, imagen, 'PequenoMundo', sku, marca, modelo, enlace, categoria)
                    producto_id = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO PrecioProducto (ProductoId, Precio) VALUES (?, ?)", producto_id, precio_valor)
                    conexion.commit()
                    cambios_detectados.append([nombre, precio_valor, marca, categoria, enlace, imagen])

            except Exception as e:
                print(f"Error procesando producto: {e}")
                continue

        print(f"✅ Página {pagina} de categoría {categoria} procesada.")
        if nuevos == 0:
            break
        pagina += 1

driver.quit()

if cambios_detectados:
    with open("cambios_pequenomundo.csv", "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Precio", "Marca", "Categoria", "UrlCompra", "Imagen"])
        writer.writerows(cambios_detectados)

print("Proceso finalizado. Total productos con cambios:", len(cambios_detectados))
