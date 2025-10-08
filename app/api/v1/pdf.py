import asyncio
from fastapi import APIRouter, UploadFile, File
import tempfile
from app.services.extract_service.enterPDF import EnterPDF

api_router = APIRouter(prefix="/pdf")

@api_router.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
        temp_file.write(await pdf.read())
        temp_file.flush()
        
        pdf_processor = EnterPDF(temp_file.name)
        pdf_data = await asyncio.to_thread(pdf_processor.process_enter)
        
    return pdf_data