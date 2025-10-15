from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.websocket import WebSocketManager
from tasks import process_pdf, process_scraping, process_ncm, process_llm

from app.core.config import settings
from app.api.router_global import api_router

ws_manager = WebSocketManager()

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

# Rota para iniciar tarefas
@app.post("/start_task/{task_name}")
async def start_task(task_name: str, websocket: WebSocket, file: UploadFile = None, pn: str = None, ncm: str = None, text: str = None):
    """
    - **task_name**: Nome da tarefa a ser executada (pdf, scraping, ncm, llm)
    - **file**: Arquivo enviado para o processamento (usado para PDF)
    - **pn**: PN do componente (usado para scraping)
    - **ncm**: Código NCM (usado para validação)
    - **text**: Texto para geração de descrição com IA (usado para LLM)
    """
    
    # Processamento de PDF
    if task_name == "pdf" and file:
        await process_pdf(websocket, file)
    # Processamento de Webscraping
    elif task_name == "scraping" and pn:
        await process_scraping(websocket, pn)
    # Validação de NCM
    elif task_name == "ncm" and ncm:
        await process_ncm(websocket, ncm)
    # Geração de Descrição com IA
    elif task_name == "llm" and text:
        await process_llm(websocket, text)
    else:
        raise HTTPException(status_code=400, detail="Parâmetros ausentes ou inválidos para a tarefa")

    return {"message": f"Tarefa {task_name} iniciada"}
