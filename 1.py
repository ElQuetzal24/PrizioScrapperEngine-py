import requests
import time

def extraer_categoria(slug):
    productos = []
    page_size = 40
    desde = 1

    session = requests.Session()
    
    # Paso 1: entrar al home como lo hace un navegador
    session.get("https://www.walmart.co.cr/", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-CR,es;q=0.9,en;q=0.8",
        "Connection": "keep-alive"
    })

    while True:
        hasta = desde + page_size - 1
        url = f"https://www.walmart.co.cr/api/catalog_system/pub/products/search/{slug}?_from={desde}&_to={hasta}&O=OrderByTopSaleDESC&sc=1"
        print(f"Categoría: {slug} [{desde}-{hasta}]")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-CR,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": f"https://www.walmart.co.cr/{slug}",
            "Origin": "https://www.walmart.co.cr",
            "Connection": "keep-alive",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        }

        try:
            res = session.get(url, headers=headers, timeout=10)

            if res.status_code == 200:
                data = res.json()
                if not data:
                    break
                productos.extend(data)
                desde += page_size
                time.sleep(0.5)
            else:
                print(f" Error HTTP {res.status_code} en {slug} [{desde}-{hasta}]")
                break

        except Exception as e:
            print(f" ❌ Error en categoría {slug}: {e}")
            break

    return productos

if __name__ == "__main__":
    productos = extraer_categoria("abarrotes/aceites-de-cocina/aceite-de-oliva")
    print(f"Total productos extraídos: {len(productos)}")
