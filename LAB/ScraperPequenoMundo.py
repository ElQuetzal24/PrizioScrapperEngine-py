import re
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import pyodbc

# Configuración de SQL Server
DB_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "localhost",
    "database": "TuBase",
    "uid": "TuUsuario",
    "pwd": "TuPassword"
}

BASE_URL = "https://tienda.pequenomundo.com"

def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']}"
    )

def guardar_productos_en_db(productos, conn):
    if not productos:
        return
    cursor = conn.cursor()
    rows = [(p["nombre"], p["precio"], p["url"], p["slug"], p["categoria"]) for p in productos]
    cursor.executemany("""
        INSERT INTO ProductosScrapeadosSimple (Nombre, Precio, Url, Slug, Categoria)
        VALUES (?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    print(f"💾 Guardados {len(rows)} productos en la base de datos.")
    cursor.close()

async def procesar_categoria(ruta, page):
    url = f"{BASE_URL}/{ruta}.html?product_list_limit=all"
    productos_data = []

    try:
        await page.goto(url, timeout=60000)
        for _ in range(5):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(1000)

        await page.wait_for_selector("li.product-item", timeout=20000)
        productos = await page.query_selector_all("li.product-item")

        for producto in productos:
            nombre_el = await producto.query_selector("a.product-item-link")
            precio_el = await producto.query_selector("span.price")

            if not nombre_el or not precio_el:
                continue

            nombre = (await nombre_el.text_content()).strip()
            precio_txt = (await precio_el.text_content()).strip().replace("₡", "").replace(",", "")
            try:
                precio = float(precio_txt)
            except:
                precio = 0.0

            href = await nombre_el.get_attribute("href")
            if not href:
                continue

            url_final = href if href.startswith("http") else BASE_URL + href
            slug = re.sub(r'\.html$', '', url_final.split("/")[-1])

            productos_data.append({
                "nombre": nombre,
                "precio": precio,
                "url": url_final,
                "slug": slug,
                "categoria": ruta
            })

        print(f"✅ {len(productos_data)} productos extraídos de /{ruta}")
        return productos_data

    except Exception as e:
        print(f"❌ Error en {ruta}: {e}")
        return []

async def main(rutas, concurrency=2):
    conn = get_db_connection()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for i in range(0, len(rutas), concurrency):
            bloque = rutas[i:i+concurrency]
            tareas = [procesar_categoria(r, page) for r in bloque]
            resultados = await asyncio.gather(*tareas)

            for productos in resultados:
                guardar_productos_en_db(productos, conn)

        await browser.close()
    conn.close()

if __name__ == "__main__":
    rutas = [
        "/abarrotes/aceites",
  "/abarrotes/articulos-de-papel",
  "/abarrotes/bebidas",
  "/abarrotes/cafe-y-te",
  "/abarrotes/cereales",
  "/abarrotes/chocolates",
  "/abarrotes/condimentos",
  "/abarrotes/confites",
  "/abarrotes/cuidado-personal",
  "/abarrotes/desechables",
  "/abarrotes/enlatados",
  "/abarrotes/envolturas",
  "/abarrotes/galletas",
  "/abarrotes/granos",
  "/abarrotes/harinas",
  "/abarrotes/jaleas",
  "/abarrotes/lacteo",
  "/abarrotes/libre-de-gluten",
  "/abarrotes/licores",
  "/abarrotes/limpieza",
  "/abarrotes/pastas",
  "/abarrotes/salsas",
  "/abarrotes/siropes",
  "/abarrotes/snacks",
  "/abarrotes/sopas-y-consomes",
  "/abarrotes/suplementos",
  "/electrodomesticos",
  "/ferreteria/acabados",
  "/ferreteria/accesorios-de-ferreteria",
  "/ferreteria/articulos-carro",
  "/ferreteria/articulos-electricos",
  "/ferreteria/articulos-para-motocicletas",
  "/ferreteria/construccion",
  "/ferreteria/herramientas",
  "/ferreteria/iluminacion",
  "/ferreteria/jardineria",
  "/ferreteria/seguridad",
  "/hogar/adornos-decoracion",
  "/hogar/alfombras",
  "/hogar/articulos-deportivos",
  "/hogar/ba-o",
  "/hogar/bebes-y-damas",
  "/hogar/camping-e-inflables",
  "/hogar/canastas",
  "/hogar/candelas-y-candelabros",
  "/hogar/ceramica",
  "/hogar/cocina",
  "/hogar/cortinas",
  "/hogar/cristaleria",
  "/hogar/dormitorio",
  "/hogar/electrodomesticos",
  "/hogar/equipo-medico",
  "/hogar/escolar-y-oficina",
  "/hogar/espejos",
  "/hogar/fiesta",
  "/hogar/juguetes-1",
  "/hogar/lavanderia",
  "/hogar/maletas",
  "/hogar/navidad",
  "/hogar/plastico",
  "/hogar/portarretratos",
  "/hogar/temporada-lluviosa",
  "/mascotas-varias/gatos",
  "/mascotas-varias/perros",
  "/muebles/bancos",
  "/muebles/camas-camarotes-y-colchones",
  "/muebles/estantes",
  "/muebles/mesas-decorativas",
  "/muebles/mesas-industriales",
  "/muebles/muebles-de-cocina",
  "/muebles/muebles-de-dormitorio",
  "/muebles/muebles-de-jardin",
  "/muebles/muebles-de-tv",
  "/muebles/muebles-infantiles",
  "/muebles/muebles-plegables",
  "/muebles/oficina",
  "/muebles/ottoman",
  "/muebles/repisas",
  "/muebles/sillas-basicas",
  "/muebles/sillon",
  "/muebles/zapateras",
  "/vacaciones",
  "/liquidaciones",
  "/mallas-construccion",
   "/mi-negocio-limpio"
    ]
    asyncio.run(main(rutas, concurrency=2))
