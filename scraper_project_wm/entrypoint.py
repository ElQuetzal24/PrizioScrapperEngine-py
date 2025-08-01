import asyncio
import os
import time
import sys
import signal
import warnings
import gc
import json  
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
    logger.info(" scraper de wal...")
    inicio = time.time()

    logger.info("1== DEBUG ENV ==")
    logger.info(f"2 srgv: {sys.argv}")
    logger.info(f"3os.environ['CATEGORIAS']: {os.getenv('CATEGORIAS')}")
    logger.info(f"4categorias parámetro inicial: {categorias}")
    logger.info(f"5DEBUG sys.argv completo: {sys.argv}")
    logger.info(f"6VALOR os.environ.get('arguments'): {os.environ.get('arguments')}")
    if len(sys.argv) > 1:
        try:
            raw_arg = sys.argv[1]
            if raw_arg.startswith("[") and raw_arg.endswith("]"):
                categorias = json.loads(raw_arg)
            else:
                categorias = [cat.strip() for cat in raw_arg.split(",") if cat.strip()]
            logger.info(f"CATEGORIAS recibidas desde argumento: {categorias}")
        except Exception as e:
            logger.warning(f"Error al interpretar argumento como categoría(s): {e}")
            categorias = []

    if not categorias:
        categorias_env = os.getenv("CATEGORIAS")
        if categorias_env:
            try:
                if categorias_env.startswith("[") and categorias_env.endswith("]"):
                    categorias = json.loads(categorias_env)
                else:
                    categorias = [cat.strip() for cat in categorias_env.split(",") if cat.strip()]
                logger.info(f"CATEGORIAS desde env: {categorias}")
            except Exception as e:
                logger.warning(f"Error al parsear CATEGORIAS desde env: {e}")
                categorias = []

    if not categorias:
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
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        raw_arg = None
        categorias = []
                
        if len(sys.argv) > 1:
            raw_arg = sys.argv[1]
            try:
                if raw_arg.startswith("[") and raw_arg.endswith("]"):
                    categorias = json.loads(raw_arg)
                else:
                    categorias = [item.strip() for item in raw_arg.split(",")]
                logger.info(f"CATEGORIAS desde sys.argv: {categorias}")
            except Exception as e:
                logger.warning(f"Error interpretando sys.argv[1]: {e}")

        loop.run_until_complete(main(categorias))

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

        try:
            asyncio.get_event_loop_policy().set_event_loop(asyncio.new_event_loop())
        except Exception:
            pass

        silence_asyncio_errors()
        sys.exit(0)
