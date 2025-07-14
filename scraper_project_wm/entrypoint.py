import asyncio
import time
from scraper import ejecutar_scraper
from categorias import CATEGORIAS
from logger import logger
import sys

async def main():
    logger.info("Lanzando scraper de Walmart")
    inicio = time.time()

    try:
        await ejecutar_scraper(CATEGORIAS, concurrencia=3)
    finally:
        fin = time.time()
        logger.info("Scraping finalizado correctamente")
        logger.info(f"Procesadas {len(CATEGORIAS)} categorías")
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
