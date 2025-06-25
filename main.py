import argparse
import asyncio
import csv

from scraper.proveedores.pequeno_mundo.scraper import PequenoMundoScraper
from scraper.proveedores.walmart.scraper import WalmartScraper
from scraper.worker import worker

async def main(args):
    queue = asyncio.Queue()

    # Lanzar 5 workers numerados
    for i in range(5):
        asyncio.create_task(worker(queue, worker_id=i+1))

    scrapers = []
    if args.pm:
        scrapers.append(PequenoMundoScraper())
    if args.walmart:
        scrapers.append(WalmartScraper())

    for scraper in scrapers:
        print(f"Ejecutando scraper: {scraper.nombre()}")
        await scraper.extraer(queue)

    # Enviar señal de parada a cada worker
    for _ in range(5):
        await queue.put(None)

    await asyncio.sleep(3)  # Esperar cierre de workers

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pm", action="store_true")
    parser.add_argument("--walmart", action="store_true")
    args = parser.parse_args()

    asyncio.run(main(args))
