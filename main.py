import argparse
import asyncio
import csv

from scrapers.sitios.pequeno_mundo.scraper import PequenoMundoScraper
from scrapers.sitios.walmart.scraper import WalmartScraper
from scrapers.sitios.walmart.scraper_api_v2 import WalmartApiV2Scraper
 

from scrapers.worker import worker

async def main(args):
    queue = asyncio.Queue()

    # Lanzar 5 workers numeradoss
    for i in range(5):
        asyncio.create_task(worker(queue, worker_id=i+1))

    scrapers = []
    if args.pm:
        scrapers.append(PequenoMundoScraper())
    if args.walmart:
        scrapers.append(WalmartScraper())
    if args.walmart_api_v2:
        scrapers.append(WalmartApiV2Scraper())


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
    parser.add_argument("--walmart_api_v2", action="store_true")
    args = parser.parse_args()

    asyncio.run(main(args))

 
