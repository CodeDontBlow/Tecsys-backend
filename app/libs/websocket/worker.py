import asyncio

task_queue = asyncio.Queue()

async def enqueue_task(func):
    await task_queue.put(func)

async def worker():
    while True:
        task_func = await task_queue.get()
        try:
            await task_func()  
            await asyncio.sleep(1)  
        except Exception as e:
            print(f"[Worker] Erro: {e}")
        finally:
            task_queue.task_done()