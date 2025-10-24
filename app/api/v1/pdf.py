import asyncio
from fastapi import APIRouter, UploadFile, File
from app.libs.websocket.manager import ws_manager
from app.libs.extract_pdf.enterPDF import EnterPDF

router = APIRouter(prefix="/pdf")

async def background_process(pdf_bytes):
    pdf_processor = EnterPDF(pdf_bytes)
    pdf_data = await asyncio.to_thread(pdf_processor.process_enter)

    await ws_manager.send_json({"status": "completed", "data": pdf_data})

@router.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    pdf_bytes = await pdf.read()

    await ws_manager.send_json({"check": "1", "status": "in_progress"})

    await ws_manager.send_json({"process": "upload_pdf","status": "in_progress"})
    pdf_processor = EnterPDF(pdf_bytes)
    await ws_manager.send_json({"process": "upload_pdf","status": "completed"})
    await ws_manager.send_json({"check": "1", "status": "completed"})

    await ws_manager.send_json({"check": "2", "status": "in_progress"})
    await ws_manager.send_json({"process": "extract_pdf","status": "in_progess"})
    await asyncio.sleep(2)
    pdf_data = await asyncio.to_thread(pdf_processor.process_enter) 
    await ws_manager.send_json({"process": "extract_pdf","status": "completed"})
    
    return pdf_data