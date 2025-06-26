import asyncio
from repositorio.sql_server import insertar_o_actualizar_producto

async def worker(queue, worker_id=1):
    print(f"Worker {worker_id} iniciado y esperando productos...")

    while True:
        producto = await queue.get()
        if producto is None:
            print(f"Worker {worker_id} ha terminado.")
            queue.task_done()
            break

        try:
            print(f"Worker {worker_id} guardando en BD: {producto[0]}")
            asyncio.create_task(asyncio.to_thread(insertar_o_actualizar_producto, *producto))
        except Exception as e:
            print(f" Error en worker {worker_id} con producto {producto[0]}: {e}")
        finally:
            queue.task_done()
