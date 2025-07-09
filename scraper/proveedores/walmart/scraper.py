
from scraper.base_scraper import IScraper
import requests
import asyncio
from repositorio.sql_server import insertar_o_actualizar_producto
from datetime import datetime

class WalmartScraper(IScraper):
    def nombre(self) -> str:
        return "Walmart"

    async def extraer(self, _):
        cambios = []
        pagina = 1
        limite = 50
        errores = 0

        log_file = "logs/walmart_errores.log"
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"\n===== INICIO DE EJECUCIÓN {datetime.now()} =====\n")

        print("Iniciando WalmartScraper...")

        while True:
            url = f"https://www.walmart.co.cr/api/catalog_system/pub/products/search?&O=OrderByTopSaleDESC&_from={(pagina-1)*limite}&_to={(pagina*limite)-1}"
            print(f"Consultando página {pagina} → {url}")
            try:
                res = requests.get(url, verify=False)
                productos = res.json()
            except Exception as e:
                mensaje = f"Error al consultar o parsear JSON: {e}"
                print(mensaje)
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(mensaje + "\n")
                break

            print(f"Productos en página {pagina}: {len(productos)}")

            if not productos:
                break

            for p in productos:
                if not isinstance(p, dict):
                    mensaje = f"Producto inválido (no es dict): {str(p)[:100]}"
                    print(mensaje)
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(mensaje + "\n")
                    errores += 1
                    if errores > 5:
                        final_msg = "Fin del Catálogo. Finalizando scraping."
                        print(final_msg)
                        with open(log_file, "a", encoding="utf-8") as log:
                            log.write(final_msg + "\n")
                        return cambios
                    continue

                try:
                    nombre = p.get("productName", "").strip()
                    precio = p["items"][0]["sellers"][0]["commertialOffer"]["Price"]
                    imagen = p["items"][0]["images"][0]["imageUrl"]
                    sku = str(p.get("productId")).strip()
                    marca = str(p.get("brand", "")).strip()
                    categoria = p.get("categories", [""])[0].strip()
                    link_text = p.get("linkText", "")
                    url_producto = f"https://www.walmart.co.cr/{link_text.strip()}/p" if link_text else ""

                    if not nombre or not precio:
                        continue

                    try:
                        precio_valor = float(precio)
                    except:
                        continue

                    print(f" Insertando en SQL: {nombre} | Precio: {precio_valor}")
                    await asyncio.to_thread(
                        insertar_o_actualizar_producto,
                        nombre, imagen, sku, marca, "", url_producto, categoria, precio_valor, "WalmartAPI"
                    )

                    cambios.append([nombre, precio, marca, categoria, url_producto, imagen])
                except Exception as e:
                    mensaje = f"Error procesando producto: {e}"
                    print(mensaje)
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(mensaje + "\n")
                    continue

            pagina += 1

        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"===== FIN DE EJECUCIÓN {datetime.now()} =====\n")

        return cambios
