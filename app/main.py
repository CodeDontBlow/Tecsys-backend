from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.websocket import WebSocketManager
from app.tasks import process_pdf, process_scraping, process_ncm, process_llm
import asyncio
from app.core.config import settings
from app.api.router_global import api_router

ws_manager = WebSocketManager()
task_queue = asyncio.Queue()

class App(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            **kwargs,
            version="0.1.0",
            title=settings.PROJECT_NAME,
            root_path=settings.ROOT_PATH
        )


app = App()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")

# Função do worker que processa as tarefas
async def worker():
    while True:
        task_func = await task_queue.get()
        if task_func is None:
            break
        await task_func()
        task_queue.task_done()

# Função para adicionar tarefas à fila
async def add_task_to_queue(task_func):
    await task_queue.put(task_func)

# Inicia worker
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(worker())

# Rota WebSocket
@app.websocket("/ws/notify")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        print("Cliente desconectado")

# Função para enviar mensagem via WebSocket
async def send_websocket_message(message: str):
    if ws_manager.active_connections: 
        await ws_manager.send_message(message)


# Modelo para validar os dados da requisição
class TaskRequest(BaseModel):
    task_name: str
    file: str = None
    pn: str = None
    ncm: str = None
    text: str = None

# Rota para iniciar tarefas
@app.post("/start_task")
async def start_task(task_request: TaskRequest):
    await send_websocket_message("PDF Carregado")

    # Verifica a tarefa e adiciona à fila
    if task_request.task_name == "pdf" and task_request.file:
        await send_websocket_message("Pegando Informações")
        await add_task_to_queue(lambda: process_pdf(task_request.file))

        await send_websocket_message("Pesquisando PN")
        await add_task_to_queue(lambda: process_scraping(task_request.pn))

        await send_websocket_message("Pesquisando Fabricante")

        await send_websocket_message("Estimando NCM")
        await add_task_to_queue(lambda: process_ncm(task_request.ncm))

        await send_websocket_message("Gerando Descrição")
        await add_task_to_queue(lambda: process_llm(task_request.text)) 

        await send_websocket_message("Processamento Completo.")

    else:
        raise HTTPException(status_code=400, detail="Parâmetros ausentes ou inválidos para a tarefa")

    return {"message": f"Tarefa {task_request.task_name} iniciada"}