import pyodbc
from loguru import logger
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar variables del .env local

def guardar_productos_scrapeados(productos: list):
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('SQL_SERVER')};"
            f"DATABASE={os.getenv('SQL_DATABASE')};"
            f"UID={os.getenv('SQL_USER')};"
            f"PWD={os.getenv('SQL_PASSWORD')};"
        )
        cursor = conn.cursor()

        registros = [
            (
                p.get("nombre", ""),
                p.get("precio", ""),
                p.get("url", ""),
                p.get("slug", ""),
                p.get("categoria", ""),
                p.get("imagen", "")
            )
            for p in productos
        ]

        cursor.executemany("""
            INSERT INTO ProductosScrapeadosSimple (Nombre, Precio, Url, Slug, Categoria, ImagenUrl)
            VALUES (?, ?, ?, ?, ?, ?)
        """, registros)

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Guardados {len(productos)} productos en la base de datos.")
    except Exception as e:
        logger.error(f"Error al guardar productos en la base de datos: {e}")