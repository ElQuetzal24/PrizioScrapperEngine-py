import asyncio
import os
from scraper import ejecutar_scraper
from logger import logger

async def main():
    logger.info("Lanzando scraper de Pequeño Mundo")

    categorias_env = os.getenv("CATEGORIAS")
    concurrencia_env = os.getenv("CONCURRENCIA", "3")

    # Parsear concurrencia
    try:
        concurrencia = int(concurrencia_env)
    except ValueError:
        logger.warning(f"Valor inválido para CONCURRENCIA: {concurrencia_env}, usando 3")
        concurrencia = 3

    # Categorías desde env o lista por defecto
    if categorias_env:
        categorias = [cat.strip() for cat in categorias_env.split(",") if cat.strip()]
        logger.info(f"CATEGORIAS desde env: {categorias}")
    else:
        from categorias import CATEGORIAS
        categorias = CATEGORIAS
        logger.info(f"Usando categorías por defecto ({len(categorias)}): {categorias[:5]}...")

    resultado = await ejecutar_scraper(categorias, concurrencia)
    logger.info(resultado)

if __name__ == "__main__":
    asyncio.run(main())
