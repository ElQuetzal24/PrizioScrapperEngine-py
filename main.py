
import argparse
import asyncio
import csv

from scraper.proveedores.pequeno_mundo.scraper import PequenoMundoScraper
from scraper.proveedores.walmart.scraper import WalmartScraper
from scraper.worker import worker

async def main(args):
    queue = asyncio.Queue()
    worker_task = asyncio.create_task(worker(queue))

    scrapers = []
    if args.pm:
        scrapers.append(PequenoMundoScraper())
    if args.walmart:
        scrapers.append(WalmartScraper())

    if not scrapers:
        print("⚠️ No se seleccionó ningún scraper. Usa --pm o --walmart")
        return

    cambios_globales = []

    for scraper in scrapers:
        print(f"🚀 Ejecutando scraper: {scraper.nombre()}")
        if scraper.nombre() == "Pequeño Mundo":
            cambios = await scraper.extraer(queue)
        else:
            cambios = await scraper.extraer(None)

        print(f"✅ {scraper.nombre()} extrajo {len(cambios)} cambios")
        cambios_globales.extend(cambios)

    print("⛔ Enviando señal de cierre al worker...")
    await queue.put(None)
    await worker_task

    if cambios_globales:
        with open("recursos/cambios_general.csv", "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre", "Precio", "Marca", "Categoria", "UrlCompra", "Imagen"])
            writer.writerows(cambios_globales)

    print(f"✅ Scraping completado. Total productos con cambios: {len(cambios_globales)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper modular por proveedor")
    parser.add_argument('--pm', action='store_true', help='Ejecutar Pequeño Mundo')
    parser.add_argument('--walmart', action='store_true', help='Ejecutar Walmart')
    args = parser.parse_args()

    asyncio.run(main(args))
