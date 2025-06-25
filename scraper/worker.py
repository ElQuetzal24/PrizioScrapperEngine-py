import asyncio
from repositorio.sql_server import insertar_o_actualizar_producto

async def worker(queue):
    while True:
        producto = await queue.get()
        if producto is None:
            break  # señal para cerrar
        try:
            await asyncio.to_thread(insertar_o_actualizar_producto, *producto)
        except Exception as e:
            print(f"❌ Error en worker al insertar producto: {e}")
        queue.task_done()
