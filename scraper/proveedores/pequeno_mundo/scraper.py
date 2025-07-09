from scraper.base_scraper import IScraper
from scraper.proveedores.pequeno_mundo. extractor import procesar_categorias
from scraper.proveedores.pequeno_mundo.navegador import crear_driver
import asyncio

# Categorías como URLs reales, no selectores CSS
CATEGORIA_URLS = [
    "abarrotes.html",
    "hogar.html",
    "muebles.html",
    "ferreteria.html",
    "mascotas.html",
    "electrodomesticos.html",
    "mallas-construccion.html",
    "mi-negocio-limpio.html"
]

class PequenoMundoScraper(IScraper):
    def nombre(self) -> str:
        return "Pequeño Mundo"

    async def extraer(self, queue):
        grupos = [CATEGORIA_URLS[i::3] for i in range(3)]
        drivers = [crear_driver() for _ in range(3)]
        tareas = [procesar_categorias(grupo, driver, queue) for grupo, driver in zip(grupos, drivers)]
        await asyncio.gather(*tareas)

        for driver in drivers:
            driver.quit()

        return []
