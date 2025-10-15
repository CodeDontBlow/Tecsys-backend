from fastapi import WebSocket
import asyncio
from app.websocket import WebSocketManager

# Instância do WebSocketManager para enviar notificações.
ws_manager = WebSocketManager()

async def process_pdf(websocket: WebSocket, pdf_file: str):
    # Extração de um PDF
    await ws_manager.send_message(f"Processando PDF: {pdf_file}")
    await asyncio.sleep(3)  # tempo simulado de processamento
    await ws_manager.send_message(f"PDF {pdf_file} extraído com sucesso!")

async def process_scraping(websocket: WebSocket, pn: str):
    # Webscraping de dados
    await ws_manager.send_message(f"Iniciando scraping com o PN: {pn}")
    await asyncio.sleep(5)  # tempo simulado do scraping
    await ws_manager.send_message(f"Scraping com PN {pn} concluído!")

async def process_ncm(websocket: WebSocket, ncm: str):
    # Validação do NCM
    await ws_manager.send_message(f"Iniciando validação de NCM: {ncm}")
    await asyncio.sleep(2)  # tempo simulado de validação
    await ws_manager.send_message(f"NCM {ncm} validado com sucesso!")

async def process_llm(websocket: WebSocket, text: str):
    # Processamento da IA
    await ws_manager.send_message(f"Iniciando geração de descrição com IA para: {text}")
    await asyncio.sleep(4)  # tempo simulado de processamento da IA
    await ws_manager.send_message(f"Descrição gerada com sucesso para: {text}")
