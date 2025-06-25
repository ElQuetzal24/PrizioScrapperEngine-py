import pyodbc

# Conexión a SQL Server
conexion = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=scrap_db;"
    "Trusted_Connection=yes;"
)
cursor = conexion.cursor()

def insertar_o_actualizar_producto(nombre, imagen, sku, marca, modelo, enlace, categoria, precio_valor):
    try:
        cursor.execute(
            "SELECT ProductoId FROM Producto WHERE Nombre = ? AND Fuente = ?",
            nombre, 'PequenoMundo'
        )
        fila = cursor.fetchone()

        if fila:
            producto_id = fila[0]
            cursor.execute(
                "SELECT TOP 1 Precio FROM PrecioProducto WHERE ProductoId = ? ORDER BY FechaRegistro DESC",
                producto_id
            )
            ultimo = cursor.fetchone()

            if not ultimo or float(ultimo[0]) != precio_valor:
                cursor.execute(
                    "INSERT INTO PrecioProducto (ProductoId, Precio) VALUES (?, ?)",
                    producto_id, precio_valor
                )
                conexion.commit()
                return True  # Cambio detectado
        else:
            cursor.execute("""
                INSERT INTO Producto (Nombre, ImagenUrl, Fuente, SKU, Marca, Modelo, UrlCompra, Categoria)
                OUTPUT INSERTED.ProductoId
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, nombre, imagen, 'PequenoMundo', sku, marca, modelo, enlace, categoria)
            producto_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO PrecioProducto (ProductoId, Precio) VALUES (?, ?)",
                producto_id, precio_valor
            )
            conexion.commit()
            return True  # Producto nuevo insertado

    except Exception as e:
        print(f"❌ Error SQL para '{nombre}': {e}")

    return False  # Sin cambios
