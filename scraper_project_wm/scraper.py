import asyncio
from navegador import lanzar_navegador
from extractor import procesar_categoria
from categorias import CATEGORIAS
from logger import logger

MAX_CONCURRENCIA = 3

async def ejecutar_scraper(categorias, concurrencia=MAX_CONCURRENCIA):
    logger.info("Lanzando scraper de Walmart")
    semaforo = asyncio.Semaphore(concurrencia)
    navegador = await lanzar_navegador()
    tareas = []
    urls_vistas = set()

    for categoria in categorias:
        page = await navegador.new_page()
        tareas.append(procesar_categoria(page, categoria, urls_vistas, semaforo))

    await asyncio.gather(*tareas)
    await navegador.close()
    logger.info("Scraping finalizado correctamente")
