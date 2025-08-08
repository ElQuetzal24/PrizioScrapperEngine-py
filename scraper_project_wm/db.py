import pyodbc
import os
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def obtener_conexion_sql():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USER')};"
        f"PWD={os.getenv('SQL_PASSWORD')};"
    )

def guardar_productos_scrapeados_masivo(productos: list):
    if not productos:
        logger.warning("No hay productos para guardar.")
        return

    try:
        conn = obtener_conexion_sql()
        cursor = conn.cursor()

 
        df = pd.DataFrame(productos)
        df["CodigoOrigen"] = "WalmartAPI"

 
        registros = list(df[["nombre", "precio", "url", "slug", "categoria", "imagen", "CodigoOrigen"]].itertuples(index=False, name=None))

 
        tvp = cursor.execute(
            "EXEC usp_ProductosScrapeados_GuardarMasivo ?",
            (registros,)
        )

        conn.commit()
        logger.info(f"Guardados {len(registros)} productos en la base de datos (masivo).")

    except Exception as e:
        logger.error(f"Error al guardar productos masivamente: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception as e:
            logger.warning(f"Error al cerrar conexión: {e}")

def guardar_productos_scrapeados(productos: list):
    if not productos:
        logger.warning("No hay productos para guardar.")
        return

    try:
        logger.debug(f"SQL_SERVER desde .env: {os.getenv('SQL_SERVER')}")
        conn = obtener_conexion_sql()
        cursor = conn.cursor()

        for p in productos:
            cursor.execute("""
                EXEC usp_ProductosScrapeados_Guardar ?, ?, ?, ?, ?, ?, ?
            """, (
                p.get("nombre", ""),
                p.get("precio", ""),
                p.get("url", ""),
                p.get("slug", ""),
                p.get("categoria", ""),
                p.get("imagen", ""),
                "WalmartAPI"  # codigoorigen
            ))

        conn.commit()
        logger.info(f"Guardados {len(productos)} productos en la base de datos.")
    except Exception as e:
        logger.error(f"Error al guardar productos con SP: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception as e:
            logger.warning(f"Error al cerrar conexión: {e}")