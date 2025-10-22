import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
from app.services.extract_service.enterPDF import EnterPDF
from app.log.logger import logger 

router = APIRouter(prefix="/pdf")


@router.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    logger.info("[PDF] POST /pdf/upload")
    logger.info(f"[PDF] Received file: {pdf.filename}")

    try:
        pdf_bytes = await pdf.read()
        pdf_processor = EnterPDF(pdf_bytes)
        pdf_data = await asyncio.to_thread(pdf_processor.process_enter)

        logger.info(f"[PDF] File processed successfully: {pdf.filename}")
        return pdf_data

    except Exception as e:
        logger.error(f"[PDF] Error processing PDF {pdf.filename}: {e}")
        raise HTTPException(status_code=500, detail="Error processing PDF file")