import asyncio
import csv
from playwright.async_api import async_playwright

async def run():
    url = "https://tienda.pequenomundo.com/hogar/fiesta.html?product_list_limit=all"
    resultados = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Cambiar a True para modo sin ventana
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        try:
            await page.locator("li.product-item").first.wait_for(timeout=15000)
        except:
            print("❌ No se encontraron productos después de esperar.")
            await browser.close()
            return

        productos = await page.locator("li.product-item").all()
        print(f"📦 Total productos encontrados: {len(productos)}\n")

        for producto in productos:
            nombre_el = await producto.query_selector("a.product-item-link")
            precio_el = await producto.query_selector("span.price")
            imagen_el = await producto.query_selector("img.product-image-photo")

            nombre = (await nombre_el.text_content()).strip() if nombre_el else "N/A"
            precio = (await precio_el.text_content()).strip() if precio_el else "N/A"
            url_producto = await nombre_el.get_attribute("href") if nombre_el else "N/A"
            imagen_url = await imagen_el.get_attribute("src") if imagen_el else "N/A"

            print(f"🛍️ {nombre} | {precio} | {url_producto} | 🖼️ {imagen_url}")

            resultados.append({
                "Nombre": nombre,
                "Precio": precio,
                "URL": url_producto,
                "Imagen": imagen_url
            })

        await browser.close()

    # Guardar en CSV
    with open("fiesta.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Nombre", "Precio", "URL", "Imagen"])
        writer.writeheader()
        writer.writerows(resultados)

    print("\n✅ Datos exportados a 'fiesta.csv' exitosamente.")

if __name__ == "__main__":
    asyncio.run(run())
