
import asyncio
from repositorio.sql_server import insertar_o_actualizar_producto

async def worker(queue):
    print("👷‍♂️ Worker iniciado y esperando productos...")

    while True:
        producto = await queue.get()
        if producto is None:
            print("🛑 Señal de cierre recibida. Terminando worker.")
            queue.task_done()
            break

        try:
            print(f"📥 Producto recibido en worker: {producto}")
            await asyncio.to_thread(insertar_o_actualizar_producto, *producto)
        except Exception as e:
            print(f"❌ Error en worker al insertar producto: {e}")
        finally:
            queue.task_done()
