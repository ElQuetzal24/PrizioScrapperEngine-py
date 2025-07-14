import asyncio
from categorias import CATEGORIAS
from scraper_project_wm.scraper import ejecutar_scraper
from logger import logger

async def main():
    logger.info("Lanzando scraper de Pequeño Mundo")
    resultado = await ejecutar_scraper(CATEGORIAS, concurrencia=3)
    logger.info("Proceso finalizado")
    logger.info(resultado)

if __name__ == "__main__":
    asyncio.run(main())
