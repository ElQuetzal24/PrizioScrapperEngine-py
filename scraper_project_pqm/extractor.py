from loguru import logger

def limpiar_slug(url):
    partes = url.split("/") if url else []
    return partes[-1] if partes else ""

async def extraer_datos_producto(element, ruta_categoria):
    try:
        nombre = await element.query_selector_eval(".product.name", "el => el.innerText")
        url_final = await element.query_selector_eval("a.product.photo", "el => el.href")
        img = await element.query_selector_eval("img.product-image-photo", "el => el.src")
        precio = await element.query_selector_eval(".price", "el => el.innerText")

        slug = limpiar_slug(url_final)

        logger.info("─────────────")
        logger.info(f" NOMBRE: {nombre.strip()}")
        logger.info(f" PRECIO: {precio.strip()}")
        logger.info(f" URL   : {url_final}")
        logger.info(f" SLUG  : {slug}")

        return {
            "nombre": nombre.strip(),
            "url": url_final,
            "imagen": img,
            "precio": precio.replace("₡", "").replace(",", "").strip(),
            "categoria": ruta_categoria,
            "slug": slug
        }

    except Exception as e:
        logger.error(f"Error al parsear producto: {e}")
        return None
