import pyodbc
from datetime import datetime

import pyodbc
from datetime import datetime


def guardar_en_bd(productos):
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=scrap_db;"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()

        for i, p in enumerate(productos):
            try:
                nombre = p.get("nombre", "") or ""
                precio = p.get("precio", "") or ""
                precio_anterior = p.get("precio_anterior", "") or ""
                sku = p.get("sku", "N/A") or "N/A"
                url = p.get("url", "") or ""
                fecha = p.get("fecha", "") or ""
                imagen = p.get("imagen", "") or ""
                categoria = p.get("categoria", "") or ""

                # Mostrar detalle del producto antes de guardar
                print(f"\n🧪 [{i}] Intentando guardar producto:")
                print(f"   Nombre: {repr(nombre)}")
                print(f"   Precio: {repr(precio)}")
                print(f"   Precioprecio_anterior: {repr(precio_anterior)}")
                print(f"   SKU: {repr(sku)}")
                print(f"   URL: {repr(url)}")
                print(f"   Fecha: {repr(fecha)}")
                print(f"   Imagen: {repr(imagen)}")
                print(f"   Categoría: {repr(categoria)}")

                cursor.execute("""
                    INSERT INTO ProductosScrapeados (Nombre, PrecioActual,PrecioAntes, SKU, Url, Fecha, Imagen, Categoria)
                    VALUES (?, ?, ?, ?, ?, ?, ?,?)
                """, nombre, precio,precio_anterior, sku, url, fecha, imagen, categoria)

            except Exception as e:
                print(f"❌ Error al guardar producto [{i}]: {e}")
                print(f"⛔ Producto con error: {p}")

        conn.commit()
        conn.close()
        print("✅ Todos los productos procesados.")

    except Exception as e:
        print(f"❌ Error general de conexión BD: {e}")


def insertar_o_actualizar_producto(nombre, imagen, sku, marca, modelo, enlace, categoria, precio_valor, fuente):
    try:
        print(f"Insertando en SQL: {nombre} | Fuente: {fuente}")
        with pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=scrap_db;"
            "Trusted_Connection=yes;"
        ) as conexion:
            cursor = conexion.cursor()

            print(f"Revisando producto: {nombre} [{fuente}]")

            cursor.execute(
                "SELECT ProductoId FROM Producto WHERE Nombre = ? AND Fuente = ?",
                nombre, fuente
            )
            fila = cursor.fetchone()

            if fila:
                producto_id = fila[0]
                cursor.execute(
                    "SELECT TOP 1 Precio FROM PrecioProducto WHERE ProductoId = ? ORDER BY FechaRegistro DESC",
                    producto_id
                )
                ultimo = cursor.fetchone()

                if not ultimo:
                    print(f"Insertando primer precio para {nombre}")
                    cursor.execute(
                        "INSERT INTO PrecioProducto (ProductoId, Precio,FechaRegistro) VALUES (?, ?, GETDATE())",
                        producto_id, precio_valor
                    )
                    conexion.commit()
                    return True
                elif float(ultimo[0]) != precio_valor:
                    print(f"Precio actualizado para {nombre}: {ultimo[0]} → {precio_valor}")
                    cursor.execute(
                        "INSERT INTO PrecioProducto (ProductoId, Precio,FechaRegistro) VALUES (?, ?, GETDATE())",
                        producto_id, precio_valor
                    )
                    conexion.commit()
                    return True
                else:
                    print(f"Precio sin cambios para {nombre}: {precio_valor}")
                    return False
            else:
                print(f"Insertando nuevo producto: {nombre}")
                cursor.execute("""
                    INSERT INTO Producto (Nombre, ImagenUrl, Fuente, SKU, Marca, Modelo, UrlCompra, Categoria)
                    OUTPUT INSERTED.ProductoId
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, nombre, imagen, fuente, sku, marca, modelo, enlace, categoria)
                producto_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO PrecioProducto (ProductoId, Precio,FechaRegistro) VALUES (?, ?, GETDATE())",
                    producto_id, precio_valor
                )
                conexion.commit()
                return True

    except Exception as e:
        print(f"Error SQL para '{nombre}': {e}")

    return False
