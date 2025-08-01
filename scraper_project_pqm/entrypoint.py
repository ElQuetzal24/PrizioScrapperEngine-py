import asyncio
import os
import time
import sys
import json

from scraper import ejecutar_scraper
from categorias import CATEGORIAS
from logger import logger

async def main(categorias):
    logger.info("Lanzando scraper de pqm...")
    inicio = time.time()

    if categorias:
        logger.info(f"CATEGORIAS recibidas desde sys.argv: {categorias}")
    else:
        categorias_env = os.getenv("CATEGORIAS")
        if categorias_env:
            categorias = [cat.strip() for cat in categorias_env.split(",") if cat.strip()]
            logger.info(f"CATEGORIAS desde env: {categorias}")
        else:
            categorias = CATEGORIAS
            logger.info(f"Usando categorías por defecto ({len(categorias)}): {categorias[:5]}...")

    concurrencia_env = os.getenv("CONCURRENCIA", "3")

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
    categorias = []

    if len(sys.argv) > 1:
        try:
            raw_arg = sys.argv[1]
            logger.info(f"sys.argv: {sys.argv}")
            if raw_arg.startswith("[") and raw_arg.endswith("]"):
                categorias = json.loads(raw_arg)
            else:
                categorias = [cat.strip() for cat in raw_arg.split(",") if cat.strip()]
        except Exception as e:
            logger.warning(f"Error interpretando sys.argv[1]: {e}")

    asyncio.run(main(categorias))
