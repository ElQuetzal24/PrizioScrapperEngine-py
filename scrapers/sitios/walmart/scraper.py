
from scrapers.base_scraper import IScraper
import requests
import asyncio
import random
from datetime import datetime
from repositorio.sql_server import insertar_o_actualizar_producto
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WalmartScraper(IScraper):
    def nombre(self) -> str:
        return "Walmart"

    async def extraer(self, _):
        cambios = []
        categorias = [
            "electrodomesticos",
            "hogar",
            "juguetes",
            "abarrotes",
            "mascotas",
            "electronica",
            "cuidado-personal"
        ]
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            "Mozilla/5.0 (Android 11; Mobile)"
        ]

        log_file = "logs/walmart_simple.log"
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"\n===== INICIO DE EJECUCIÓN {datetime.now()} =====\n")

        for categoria in categorias:
            print(f"\nCategoría: {categoria}")
            pagina = 0

            while True:
                _from = pagina * 50
                _to = _from + 49
                if _to > 2500:
                    break

                url = (
                    f"https://www.walmart.co.cr/api/catalog_system/pub/products/search/{categoria}"
                    f"?_from={_from}&_to={_to}&O=OrderByNameASC&sc=1"
                )
                headers = {
                    "User-Agent": random.choice(user_agents),
                    "Accept": "application/json"
                }

                print(f" Página {pagina} → {_from}-{_to}")
                try:
                    res = requests.get(url, headers=headers, timeout=10, verify=False)
                    if res.status_code != 200:
                        print(f" Error HTTP {res.status_code}. Saltando categoría.")
                        break

                    productos = res.json()
                    if not productos:
                        print(" Fin de productos en esta categoría.")
                        break

                    for p in productos:
                        try:
                            nombre = p.get("productName", "").strip()
                            sku = str(p.get("productId", "")).strip()
                            marca = str(p.get("brand", "")).strip()
                            categoria_wm = p.get("categories", [""])[0].strip()
                            imagen = p.get("items", [{}])[0].get("images", [{}])[0].get("imageUrl", "")
                            precio = p.get("items", [{}])[0].get("sellers", [{}])[0].get("commertialOffer", {}).get("Price", 0)
                            precio_lista = p.get("items", [{}])[0].get("sellers", [{}])[0].get("commertialOffer", {}).get("ListPrice", 0)
                            stock = p.get("items", [{}])[0].get("sellers", [{}])[0].get("commertialOffer", {}).get("AvailableQuantity", 0)
                            ean = p.get("items", [{}])[0].get("ean", "")
                            link_text = p.get("linkText", "")
                            url_producto = f"https://www.walmart.co.cr/{link_text.strip()}/p" if link_text else ""

                            if not nombre or not precio:
                                continue

                            precio_valor = float(precio)
                            precio_original = float(precio_lista) if precio_lista else precio_valor

                            print(f" Insertando: {nombre} | Precio: {precio_valor}")
                            await asyncio.to_thread(
                                insertar_o_actualizar_producto,
                                nombre, imagen, sku, marca, ean, url_producto, categoria_wm,
                                precio_valor, "WalmartAPI"
                            )
                            cambios.append({
                                "nombre": nombre,
                                "sku": sku,
                                "marca": marca,
                                "precio": precio_valor,
                                "precio_original": precio_original,
                                "stock": stock,
                                "imagen": imagen,
                                "url": url_producto,
                                "categoria": categoria_wm
                            })
                        except Exception as e:
                            print(f" Error procesando producto: {e}")
                            with open(log_file, "a", encoding="utf-8") as log:
                                log.write(f" Error procesando producto: {e}\n")
                            continue

                    pagina += 1
                    await asyncio.sleep(random.uniform(0.5, 1.2))

                except requests.RequestException as e:
                    print(f" RequestException: {e}")
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(f" RequestException: {e}\n")
                    break

        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"===== FIN DE EJECUCIÓN {datetime.now()} =====\n")

        return cambios
