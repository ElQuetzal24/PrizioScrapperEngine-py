from scraper.navegador import crear_driver
from scraper.extractor import procesar_categorias, CATEGORIA_SELECTORES
from scraper.worker import worker
import asyncio
from datetime import datetime
import csv

async def main():
    queue = asyncio.Queue()

    # Dividir las categorías en 3 grupos para procesarlas en paralelo
    grupos = [CATEGORIA_SELECTORES[i::3] for i in range(3)]
    drivers = [crear_driver() for _ in range(3)]

    # Lanzar el worker
    worker_task = asyncio.create_task(worker(queue))

    # Ejecutar scraping en paralelo
    tareas_scraping = [
        procesar_categorias(grupo, driver, queue)
        for grupo, driver in zip(grupos, drivers)
    ]
    resultados = await asyncio.gather(*tareas_scraping)

    # Cerrar cola y esperar al worker
    await queue.put(None)
    await worker_task

    for driver in drivers:
        driver.quit()

    # Unir todos los cambios
    cambios = [item for sublist in resultados for item in sublist]

    if cambios:
        with open("recursos/cambios_pm.csv", "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre", "Precio", "Marca", "Categoria", "UrlCompra", "Imagen"])
            writer.writerows(cambios)

    print(f"🎯 Proceso finalizado. Total productos con cambios: {len(cambios)}")

if __name__ == "__main__":
    asyncio.run(main())
