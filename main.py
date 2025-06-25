from scraper.navegador import crear_driver
from scraper.extractor import procesar_categorias
import asyncio

async def main():
    driver = crear_driver()
    cambios = await procesar_categorias(driver)
    driver.quit()

    if cambios:
        from datetime import datetime
        import csv
        with open("recursos/cambios_pm.csv", "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre", "Precio", "Marca", "Categoria", "UrlCompra", "Imagen"])
            writer.writerows(cambios)

    print(f"🎯 Proceso finalizado. Total productos con cambios: {len(cambios)}")

if __name__ == "__main__":
     asyncio.run(main())
