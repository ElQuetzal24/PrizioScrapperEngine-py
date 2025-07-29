import asyncio
import os
import time
from scraper import ejecutar_scraper
from categorias import CATEGORIAS
from logger import logger
import sys

async def main():
    logger.info("Lanzando scraper de Walmart")
    inicio = time.time()

    categorias_env = os.getenv("CATEGORIAS")
    concurrencia_env = os.getenv("CONCURRENCIA", "3")

    try:
        concurrencia = int(concurrencia_env)
    except ValueError:
        logger.warning(f"Valor inválido para CONCURRENCIA: {concurrencia_env}, usando 3")
        concurrencia = 3

    if categorias_env:
        categorias = [cat.strip() for cat in categorias_env.split(",") if cat.strip()]
        logger.info(f"CATEGORIAS desde env: {categorias}")
    else:
        categorias = CATEGORIAS
        logger.info(f"Usando categorías por defecto ({len(categorias)}): {categorias[:5]}...")

    try:
        await ejecutar_scraper(categorias, concurrencia=concurrencia)
    finally:
        fin = time.time()
        logger.info("Scraping finalizado correctamente")
        logger.info(f"Procesadas {len(categorias)} categorías")
        logger.info(f"Tiempo total: {round(fin - inicio, 2)} segundos")

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Scraper interrumpido manualmente.")
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        sys.exit(0)
