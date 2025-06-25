from repositorio.sql_server import insertar_o_actualizar_producto
import asyncio

async def worker(queue, worker_id=1):
    print(f"Worker {worker_id} iniciado y esperando productos...")

    while True:
        producto = await queue.get()
        if producto is None:
            break

        try:
            print(f"Worker {worker_id} guardando en BD: {producto[0]}")
            await asyncio.to_thread(insertar_o_actualizar_producto, *producto)
        except Exception as e:
            print(f"❌ Error en worker {worker_id}: {e}")
