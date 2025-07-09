import asyncio
import random
import time
import requests
import urllib3

from scraper.base_scraper import IScraper
from repositorio.sql_server import insertar_o_actualizar_producto

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WalmartApiV2Scraper(IScraper):
    def nombre(self):
        return "WalmartAPIv2"

    async def extraer(self, queue):
        print("🧭 Ejecutando Walmart API v2...")

        categorias = [
            "electrodomesticos",
            "electronica",
            "hogar",
            "abarrotes",
            "cuidado-personal",
            "juguetes",
            "mascotas"
        ]

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            "Mozilla/5.0 (Android 11; Mobile)"
        ]

        for categoria in categorias:
            print(f"\n📂 Categoría: {categoria}")
            pagina = 0
            errores_consecutivos = 0
            vacios_consecutivos = 0

            while True:
                _from = pagina * 40
                _to = _from + 39

                url = (
                    f"https://www.walmart.co.cr/api/catalog_system/pub/products/search?"
                    f"fq=C:{categoria}&_from={_from}&_to={_to}"
                )

                headers = {
                    "User-Agent": random.choice(user_agents),
                    "Accept": "application/json"
                }

                print(f"🔍 Página {pagina} → {_from}-{_to}")
                try:
                    res = requests.get(url, headers=headers, timeout=10, verify=False)

                    if res.status_code == 206:
                        print("⚠️ 206 Partial Content. Reintentando con backoff...")
                        errores_consecutivos += 1
                        await asyncio.sleep(2 * errores_consecutivos)
                        if errores_consecutivos > 3:
                            print("🚫 Demasiados errores 206. Siguiente categoría.")
                            break
                        continue

                    if res.status_code != 200:
                        print(f"❌ HTTP {res.status_code}. Deteniendo categoría.")
                        break

                    productos = res.json()
                    if not productos:
                        vacios_consecutivos += 1
                        if vacios_consecutivos >= 2:
                            print("✅ Fin de productos en esta categoría.")
                            break
                        else:
                            pagina += 1
                            continue

                    for prod in productos:
                        try:
                            nombre = prod.get("productName")
                            sku = prod.get("productId")
                            marca = prod.get("brand")
                            imagen = prod.get("items", [{}])[0].get("images", [{}])[0].get("imageUrl", "")
                            precio = prod.get("items", [{}])[0].get("sellers", [{}])[0].get("commertialOffer", {}).get("Price", 0)
                            link = prod.get("linkText", "")
                            url_producto = f"https://www.walmart.co.cr/{link}"

                            if not nombre or not sku or not precio:
                                continue

                            await queue.put({
                                "nombre": nombre,
                                "sku": sku,
                                "marca": marca,
                                "imagen": imagen,
                                "precio": precio,
                                "url": url_producto,
                                "categoria": categoria,
                                "fuente": "WalmartAPI"
                            })
                        except Exception as e:
                            print(f"⚠️ Error interno al procesar producto: {e}")

                    pagina += 1
                    errores_consecutivos = 0
                    vacios_consecutivos = 0
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                except requests.RequestException as e:
                    print(f"❌ RequestException: {e}")
                    errores_consecutivos += 1
                    await asyncio.sleep(2 * errores_consecutivos)
                    if errores_consecutivos > 3:
                        print("🚫 Demasiados errores seguidos. Siguiente categoría.")
                        break
