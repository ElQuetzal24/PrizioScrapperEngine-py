import asyncio
import os
import time
from scraper import ejecutar_scraper
from categorias import CATEGORIAS
from logger import logger

async def main(categorias):
    logger.info("Lanzando scraper de pqm...")
    inicio = time.time()

    # Si las categorías vienen desde el orquestador, las usamos
    if categorias:
        logger.info(f"CATEGORIAS recibidas desde el orquestador: {categorias}")
    else:
        # Si no, seguimos con las categorías de las variables de entorno o por defecto
        categorias_env = os.getenv("CATEGORIAS")
        if categorias_env:
            categorias = [cat.strip() for cat in categorias_env.split(",") if cat.strip()]
            logger.info(f"CATEGORIAS desde env: {categorias}")
        else:
            categorias = CATEGORIAS
            logger.info(f"Usando categorías por defecto ({len(categorias)}): {categorias[:5]}...")

    concurrencia_env = os.getenv("CONCURRENCIA", "3")

    # Parsear concurrencia
    try:
        concurrencia = int(concurrencia_env)
    except ValueError:
        logger.warning(f"Valor inválido para CONCURRENCIA: {concurrencia_env}, usando 3")
        concurrencia = 3

    try:
        await ejecutar_scraper(categorias, concurrencia=concurrencia)
    finally:
        fin = time.time()
        logger.info("Scraping finalizado correctamente")
        logger.info(f"Procesadas {len(categorias)} categorías")
        logger.info(f"Tiempo total: {round(fin - inicio, 2)} segundos")

if __name__ == "__main__":
    #categorias_fn = None Simulación local
    #if categorias_fn is None: Simulación local
        #categorias_fn = ["/hogar/fiesta"]  Simulación local  

    #asyncio.run(main(categorias_fn)) Simulación local
    asyncio.run(main([]))