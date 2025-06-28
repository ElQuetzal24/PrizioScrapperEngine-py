import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import pyodbc
from datetime import datetime
 

CATEGORIA_URL = "https://www.walmart.co.cr/articulos-para-el-hogar?page="
MAX_PAGINAS = 1
FUENTE = "WalmartCR"

# Configura tu cadena de conexión aquí
CONN_STRING = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=scrap_db;"
            "Trusted_Connection=yes;"
)

def guardar_en_bd(productos):
    try:
        try:
            from tqdm import tqdm
        except ImportError:
            # Si tqdm no está instalado, usar un iterador normal
            def tqdm(x, **kwargs):
                return x

        conn = pyodbc.connect(CONN_STRING)
        cursor = conn.cursor()
        total = len(productos)
        print(f"🔄 Procesando {total} productos...")
        for i, p in enumerate(tqdm(productos, desc="➡ Guardando", unit="producto"), start=1):
            try:
                cursor.execute("""
                    INSERT INTO Producto (Nombre, Precio, SKU, UrlCompra, Fuente, FechaCreacion)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, 
                p["nombre"], 
                parsear_precio(p["precio"]),
                p["sku"], 
                p["url"], 
                FUENTE, 
                datetime.now())
            except Exception as e:
                print(f"❌ Error en producto {i}/{total}: {e}")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Guardado completo de {total} productos.")
    except Exception as e:
        print(f"❌ Error al conectar o guardar en base de datos: {e}")


def parsear_precio(pstr):
    try:
        if not pstr or pstr == "N/A":
            return None
        limpio = pstr.replace("₡", "").replace(",", "").strip()
        if limpio.count(".") > 1:
            limpio = limpio.replace('.', '', limpio.count('.') - 1)
        return float(limpio)
    except:
        return None
    
async def extraer_productos(page, pagina):
    url = f"{CATEGORIA_URL}{pagina}"
    await page.goto(url, timeout=60000)
    await page.wait_for_selector(".vtex-search-result-3-x-galleryItem", timeout=15000)
    await scroll_hasta_cargar_todos(page)

    items = page.locator(".vtex-search-result-3-x-galleryItem")
    total = await items.count()
    productos = []

    for i in range(total):
        item = items.nth(i)
        nombre = await item.locator("a span").first.text_content()
        precio = await item.locator("[class*=price]").first.text_content()
        link = await item.locator("a").first.get_attribute("href")

        productos.append({
            "nombre": nombre.strip() if nombre else "N/A",
            "precio": precio.strip().replace("₡", "").replace(",", "") if precio else "N/A",
            "sku": "N/A",
            "url": f"https://www.walmart.co.cr{link}" if link else "N/A"
        })
    return productos

async def scroll_hasta_cargar_todos(page):
    productos_antes = 0
    while True:
        await page.mouse.wheel(0, 2000)
        await page.wait_for_timeout(1500)
        productos_actuales = await page.locator(".vtex-search-result-3-x-galleryItem").count()
        if productos_actuales == productos_antes:
            break
        productos_antes = productos_actuales


async def main():
    ultima_pagina_exitosa = 1
    try:
        with open("ultima_pagina.txt", "r") as f:
            ultima_pagina_exitosa = int(f.read().strip())
    except:
        pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for pagina in range(ultima_pagina_exitosa, MAX_PAGINAS + 1):
            try:
                print(f"🌀 Página {pagina}")
                productos = await extraer_productos(page, pagina)
                print(f"✅ Productos extraídos: {len(productos)}")
                guardar_en_bd(productos)

                with open("ultima_pagina.txt", "w") as f:
                    f.write(str(pagina + 1))

            except Exception as e:
                print(f"❌ Error en la página {pagina}: {e}")
                break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
