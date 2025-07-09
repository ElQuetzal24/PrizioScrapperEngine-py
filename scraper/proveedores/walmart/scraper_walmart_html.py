import requests
from bs4 import BeautifulSoup
from scraper.base_scraper import IScraper
from repositorio.sql_server import insertar_o_actualizar_producto
import time

class WalmartHTMLScraper(IScraper):
    @property
    def nombre(self):
        return "WalmartHTML"

    def extraer(self):
        categorias = [
            "abarrotes", "hogar", "muebles", "ferreteria", "mascotas",
            "electrodomesticos", "mallas-construccion", "mi-negocio-limpio"
        ]
        base_url = "https://www.walmart.co.cr/c/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        for categoria in categorias:
            url_categoria = f"{base_url}{categoria}"
            print(f" Procesando categoría: {categoria}")
            try:
                res = requests.get(url_categoria, headers=headers, timeout=10)
                if res.status_code != 200:
                    print(f" Error HTTP {res.status_code} en {url_categoria}")
                    continue

                soup = BeautifulSoup(res.text, "html.parser")
                productos = soup.select(".vtex-product-summary-2-x-container")

                for prod in productos:
                    nombre = prod.select_one(".vtex-product-summary-2-x-productBrand").text.strip() + " " +                              prod.select_one(".vtex-product-summary-2-x-productName").text.strip()
                    enlace_tag = prod.select_one("a.vtex-product-summary-2-x-clearLink")
                    enlace = "https://www.walmart.co.cr" + enlace_tag["href"] if enlace_tag else ""
                    precio_tag = prod.select_one("span.vtex-product-price-1-x-currencyContainer > span")
                    precio = precio_tag.text.strip().replace("₡", "").replace(",", "") if precio_tag else "0"
                    imagen_tag = prod.select_one("img.vtex-product-summary-2-x-imageNormal")
                    imagen = imagen_tag["src"] if imagen_tag else ""

                    insertar_o_actualizar_producto(
                        nombre=nombre,
                        imagen=imagen,
                        sku=None,
                        marca=None,
                        modelo=None,
                        enlace=enlace,
                        categoria=categoria,
                        precio_valor=float(precio),
                        fuente="WalmartHTML"
                    )
                    print(f" {nombre} | ₡{precio}")
                    time.sleep(0.1)
            except Exception as e:
                print(f" Error en categoría {categoria}: {e}")