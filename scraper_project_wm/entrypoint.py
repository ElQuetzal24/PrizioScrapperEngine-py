import asyncio
import os
import time
import sys
import signal
import warnings
import gc

from scraper import ejecutar_scraper
from categorias import CATEGORIAS
from logger import logger

 
warnings.simplefilter("ignore", ResourceWarning)

 
def silence_asyncio_errors():
    gc.collect()
    for obj in gc.get_objects():
        try:
            if isinstance(obj, asyncio.BaseTransport):
                obj._loop = None
        except Exception:
            pass

async def main(categorias):
    logger.info("Lanzando scraper de wal...")
    inicio = time.time()

    if categorias:
        logger.info(f"CATEGORIAS recibidas desde el orquestador: {categorias}")
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
    categorias_fn = None
    if categorias_fn is None:
        categorias_fn = ["lo-nuevo"]  # Simulación local

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        signal.signal(signal.SIGINT, signal.SIG_DFL) 

        loop.run_until_complete(main(categorias_fn))
    except KeyboardInterrupt:
        print("Scraper interrumpido manualmente.")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()

        # Fix final para errores de __del__ en objetos asyncio (Windows/Python 3.12)
        try:
            asyncio.get_event_loop_policy().set_event_loop(asyncio.new_event_loop())
        except Exception:
            pass

        silence_asyncio_errors()
        sys.exit(0)

