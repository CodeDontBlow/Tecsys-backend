from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, UploadFile, File, Depends
from app.db.database import get_session
from app.libs.websocket.worker import enqueue_task
from app.pipeline.flow_pipeline import PipelineManager

router = APIRouter(prefix="/pdf")

@router.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...), db_session: AsyncSession = Depends(get_session)):
    pdf_bytes = await pdf.read()

    order_date = datetime.now(timezone.utc)


    manager = PipelineManager(pdf_bytes, db_session, order_date)

    await enqueue_task(manager.run)

    return {
        "message": "Upload recebido com sucesso. Processamento iniciado em background.",
        "file_name": pdf.filename,
    }
