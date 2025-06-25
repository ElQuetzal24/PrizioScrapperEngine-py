import asyncio
from scraper.base_scraper import IScraper
from scraper.proveedores.pequeno_mundo.navegador import crear_driver
from scraper.proveedores.pequeno_mundo.extractor import procesar_categorias, CATEGORIA_SELECTORES

class PequenoMundoScraper(IScraper):
    def nombre(self) -> str:
        return "Pequeño Mundo"

    async def extraer(self, queue):
        grupos = [CATEGORIA_SELECTORES[i::3] for i in range(3)]
        drivers = [crear_driver() for _ in range(3)]

        tareas = [procesar_categorias(grupo, driver, queue) for grupo, driver in zip(grupos, drivers)]
        resultados = await asyncio.gather(*tareas)

        for driver in drivers:
            driver.quit()

        return [item for sublist in resultados for item in sublist]
