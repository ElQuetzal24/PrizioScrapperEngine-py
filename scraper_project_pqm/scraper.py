import asyncio
from navegador import procesar_categoria
from logger import logger

async def ejecutar_scraper(categorias, concurrencia=3):
    logger.info(f"Iniciando scraping con {len(categorias)} categorías (concurrencia {concurrencia})")
    sem = asyncio.Semaphore(concurrencia)
    await asyncio.gather(*(procesar_categoria(ruta, sem) for ruta in categorias))
    logger.info("Scraping finalizado correctamente")
    return f"Procesadas {len(categorias)} categorías"
