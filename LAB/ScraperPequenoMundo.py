import sys
import json
import asyncio
from playwright.async_api import async_playwright
import pyodbc
from datetime import datetime

# Leer argumentos desde línea de comandos
if len(sys.argv) < 3:
    print("❌ Debes pasar la lista de categorías y la concurrencia como argumentos.")
    sys.exit(1)

try:
    RUTAS = json.loads(sys.argv[1])  # lista como string JSON
    CONCURRENCY = int(sys.argv[2])
except Exception as e:
    print(f"❌ Error leyendo argumentos: {e}")
    sys.exit(1)

BASE = "https://tienda.pequenomundo.com"

async def procesar_categoria(ruta: str, sem: asyncio.Semaphore):
    url = f"{BASE}/{ruta}.html?product_list_limit=all"
    async with sem:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="es-CR"
            )
            page = await context.new_page()
            print(f"\n🌐 Procesando: /{ruta}")
            try:
                await page.goto(url, timeout=60000)
                for _ in range(5):
                    await page.mouse.wheel(0, 4000)
                    await page.wait_for_timeout(1000)

                await page.wait_for_selector("li.product-item", timeout=20000)
            except Exception as e:
                print(f"❌ Sin productos o error en /{ruta} → {e}")
                await browser.close()
                return

            productos = await page.query_selector_all("li.product-item")
            print(f"✅ {len(productos)} productos en /{ruta}")

            for producto in productos:
                nombre_el = await producto.query_selector("a.product-item-link")
                precio_el = await producto.query_selector("span.price")

                nombre = (await nombre_el.text_content()).strip() if nombre_el else "N/A"
                precio = (await precio_el.text_content()).strip() if precio_el else "N/A"

                href = await nombre_el.get_attribute("href") if nombre_el else ""
                url_final = href if href.startswith("http") else BASE + href
                slug = href.strip().split("/")[-1].replace(".html", "") if href else "N/A"

                print("─────────────")
                print("🛍️ NOMBRE:", nombre)
                print("💵 PRECIO:", precio)
                print("🔗 URL   :", url_final)
                print("🔖 SLUG  :", slug)

            await browser.close()

async def main():
    sem = asyncio.Semaphore(CONCURRENCY)
    await asyncio.gather(*(procesar_categoria(ruta, sem) for ruta in RUTAS))

if __name__ == "__main__":
    asyncio.run(main())
import sys
import json
import asyncio
from playwright.async_api import async_playwright

# Leer argumentos desde línea de comandos
if len(sys.argv) < 3:
    print("❌ Debes pasar la lista de categorías y la concurrencia como argumentos.")
    sys.exit(1)

try:
    RUTAS = json.loads(sys.argv[1])  # lista como string JSON
    CONCURRENCY = int(sys.argv[2])
except Exception as e:
    print(f"❌ Error leyendo argumentos: {e}")
    sys.exit(1)

BASE = "https://tienda.pequenomundo.com"


def guardar_productos_scrapeados(productos: list):
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-S5C78JU;"                 # Cambiar si usás otro host
        "DATABASE=Scrap_db;"          # Reemplazá con tu base
        "UID=sa;"                   # Usuario de SQL Server
        "PWD=ABC123xyz;"               # Contraseña
    )
    cursor = conn.cursor()

    for p in productos:
        cursor.execute("""
            INSERT INTO ProductosScrapeadosSimple (Nombre, Precio, Url, Slug,Categoria)
            VALUES (?, ?, ?, ?, ?)
        """, 
        p["nombre"],
        p.get("precio",""),
        p.get("url", ""),
        p.get("slug", ""),
         p.get("categoria", "")
        )

    conn.commit()
    cursor.close()
    conn.close()


async def procesar_categoria(ruta: str, sem: asyncio.Semaphore):
    url = f"{BASE}/{ruta}.html?product_list_limit=all"
    async with sem:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="es-CR"
            )
            page = await context.new_page()
            print(f"\n🌐 Procesando: /{ruta}")
            try:
                await page.goto(url, timeout=60000)
                for _ in range(5):
                    await page.mouse.wheel(0, 4000)
                    await page.wait_for_timeout(1000)

                await page.wait_for_selector("li.product-item", timeout=20000)
            except Exception as e:
                print(f"❌ Sin productos o error en /{ruta} → {e}")
                await browser.close()
                return

            productos = await page.query_selector_all("li.product-item")
            print(f"✅ {len(productos)} productos en /{ruta}")

            productos_data = []
            for producto in productos:
                nombre_el = await producto.query_selector("a.product-item-link")
                precio_el = await producto.query_selector("span.price")

                nombre = (await nombre_el.text_content()).strip() if nombre_el else "N/A"
                precio = (await precio_el.text_content()).strip() if precio_el else "N/A"

                href = await nombre_el.get_attribute("href") if nombre_el else ""
                url_final = href if href.startswith("http") else BASE + href
                slug = href.strip().split("/")[-1].replace(".html", "") if href else "N/A"

                print("─────────────")
                print("🛍️ NOMBRE:", nombre)
                print("💵 PRECIO:", precio)
                print("🔗 URL   :", url_final)
                print("🔖 SLUG  :", slug)

                productos_data.append({
                    "nombre": nombre,
                    "precio": precio,
                    "url": url_final,
                    "slug": slug,
                    "categoria": ruta
                    
                     
                })


            await browser.close()

            if productos_data:
                guardar_productos_scrapeados(productos_data)


async def main():
    sem = asyncio.Semaphore(CONCURRENCY)
    await asyncio.gather(*(procesar_categoria(ruta, sem) for ruta in RUTAS))

if __name__ == "__main__":
    asyncio.run(main())
