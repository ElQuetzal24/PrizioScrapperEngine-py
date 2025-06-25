import pyodbc

def insertar_o_actualizar_producto(nombre, imagen, sku, marca, modelo, enlace, categoria, precio_valor, fuente):
    try:
        print(f"➡️ Insertando en SQL: {nombre} | Fuente: {fuente}")
        with pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=scrap_db;"
            "Trusted_Connection=yes;"
        ) as conexion:
            cursor = conexion.cursor()

            print(f"📥 Revisando producto: {nombre} [{fuente}]")

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
                    print(f"➕ Insertando primer precio para {nombre}")
                    cursor.execute(
                        "INSERT INTO PrecioProducto (ProductoId, Precio,FechaRegistro) VALUES (?, ?, GETDATE())",
                        producto_id, precio_valor
                    )
                    conexion.commit()
                    return True
                elif float(ultimo[0]) != precio_valor:
                    print(f"🔁 Precio actualizado para {nombre}: {ultimo[0]} → {precio_valor}")
                    cursor.execute(
                        "INSERT INTO PrecioProducto (ProductoId, Precio,FechaRegistro) VALUES (?, ?, GETDATE())",
                        producto_id, precio_valor
                    )
                    conexion.commit()
                    return True
                else:
                    print(f"🟰 Precio sin cambios para {nombre}: {precio_valor}")
                    return False
            else:
                print(f"🆕 Insertando nuevo producto: {nombre}")
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
        print(f"❌ Error SQL para '{nombre}': {e}")

    return False
