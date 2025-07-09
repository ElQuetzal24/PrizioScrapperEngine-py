import requests
import asyncio
import random
import json
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WalmartScraperV2:
    def __init__(self):
        self.base_url = "https://www.walmart.co.cr"
        self.search_api = f"{self.base_url}/api/catalog_system/pub/products/search"
        self.category_api = f"{self.base_url}/api/catalog_system/pub/category/tree/3"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            "Mozilla/5.0 (Android 11; Mobile)"
        ]
        self.output_file = "walmart_productos.json"
        self.log_file = "logs/walmart_scraper_v2.log"

    def log(self, msg):
        print(msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    def get_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "application/json"
        }

    def get_all_category_urls(self):
        try:
            res = requests.get(self.category_api, headers=self.get_headers(), timeout=10)
            res.raise_for_status()
            categorias = []

            def recorrer(nodos, ruta=""):
                for nodo in nodos:
                    url = nodo.get("url", "").strip("/")
                    if url:
                        categorias.append(url)
                    if "children" in nodo:
                        recorrer(nodo["children"], ruta + "/" + url)

            data = res.json()
            recorrer(data)
            return categorias
        except Exception as e:
            self.log(f"Error obteniendo categorías: {e}")
            return []

    async def extraer_categoria(self, slug):
        productos = []
        pagina = 0
        self.log(f"\nCategoría: {slug}")

        while True:
            _from = pagina * 50
            _to = _from + 49
            if _to > 2500:
                break

            url = f"{self.search_api}/{slug}?_from={_from}&_to={_to}&sc=1"
            try:
                res = requests.get(url, headers=self.get_headers(), timeout=10, verify=False)
                if res.status_code == 206:
                    self.log(f" HTTP 206 en {slug} [{_from}-{_to}]. Saltando.")
                    break
                if res.status_code != 200:
                    self.log(f" Error HTTP {res.status_code} en {slug} [{_from}-{_to}].")
                    break

                data = res.json()
                if not data:
                    break

                for p in data:
                    try:
                        item = {
                            "nombre": p.get("productName", "").strip(),
                            "sku": str(p.get("productId", "")).strip(),
                            "marca": p.get("brand", "").strip(),
                            "categoria": p.get("categories", [""])[0].strip(),
                            "url": f"{self.base_url}/{p.get('linkText', '')}/p",
                            "imagen": p.get("items", [{}])[0].get("images", [{}])[0].get("imageUrl", ""),
                            "precio": p.get("items", [{}])[0].get("sellers", [{}])[0].get("commertialOffer", {}).get("Price", 0),
                            "precio_original": p.get("items", [{}])[0].get("sellers", [{}])[0].get("commertialOffer", {}).get("ListPrice", 0),
                            "stock": p.get("items", [{}])[0].get("sellers", [{}])[0].get("commertialOffer", {}).get("AvailableQuantity", 0),
                            "ean": p.get("items", [{}])[0].get("ean", "")
                        }
                        productos.append(item)
                    except Exception as e:
                        self.log(f"  Error en producto: {e}")
                        continue

                pagina += 1
                await asyncio.sleep(random.uniform(0.4, 1.2))
            except Exception as e:
                self.log(f"  Error consultando productos: {e}")
                break
        return productos

    async def ejecutar(self):
        self.log(f"===== INICIO {datetime.now()} =====")
        categorias = self.get_all_category_urls()
        self.log(f"Total categorías detectadas: {len(categorias)}")
        resultados = []

        for cat in categorias:
            productos = await self.extraer_categoria(cat)
            resultados.extend(productos)

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)

        self.log(f"Total productos extraídos: {len(resultados)}")
        self.log(f"===== FIN {datetime.now()} =====")


if __name__ == "__main__":
    scraper = WalmartScraperV2()
    asyncio.run(scraper.ejecutar())
