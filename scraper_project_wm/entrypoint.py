import asyncio
from categorias import CATEGORIAS
from scraper import ejecutar_scraper

async def main():
    print("🚀 Iniciando scraping Walmart...")
    resultado = await ejecutar_scraper(CATEGORIAS, concurrencia=3)
    print("✅ Finalizado Walmart")
    print(resultado)

if __name__ == "__main__":
    asyncio.run(main())
