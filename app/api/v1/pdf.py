import asyncio
from fastapi import APIRouter, UploadFile, File
from app.libs.websocket.worker import enqueue_task
from app.pipeline.flow_pipeline import PipelineManager

router = APIRouter(prefix="/pdf")

@router.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    pdf_bytes = await pdf.read()

    manager = PipelineManager(pdf_bytes)

    await enqueue_task(manager.run)

    return {
        "message": "Upload recebido com sucesso. Processamento iniciado em background.",
        "file_name": pdf.filename,
    }
