from unittest import result
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.controllers.product_router import router as product_router
from app.api.controllers.manufacturer_router import router as manufacturer_router
from app.api.controllers.supplyer_router import router as supplyer_router
from app.core.dependencies import DatabaseDependency
from app.services.extract_service.enterPDF import EnterPDF
from app.services.ncm_service import get_ncm
from app.services.ollama_service.generate_final_desc import Generate_final_desc

api_router = APIRouter()

api_router.include_router(product_router, prefix="/products", tags=["products"])
api_router.include_router(
    manufacturer_router, prefix="/manufacturer", tags=["manufacturer"]
)
api_router.include_router(supplyer_router, prefix="/supplyer", tags=["supplyer"])


# Database route for health check
@api_router.get("/ping-db")
async def ping_db(db: DatabaseDependency):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@api_router.post("/upload_pdf")
async def run_flow(pdf: UploadFile = File(...)
                   , description: str = Form(...)
                   ):
    
    embeeding_object = get_ncm(description)

    # START PDF AND LLM FLOW
    pdf_bytes = await pdf.read()

    pdf_object = EnterPDF(pdf_bytes=pdf_bytes)

    pdf_object.process_enter()

    products_descs = pdf_object.get_erp_desc()

    test = ['01']
    products_descs = {k: products_descs[k] for k in test if k in products_descs}
    print(products_descs)

    llm_results = await Generate_final_desc.generate_final_desc_async(products_descs)
    # FINISH PDF AND LLM FLOW

    return JSONResponse({
        "ai-description": llm_results,
        "embeeding": embeeding_object
        # {
        #     "original_query": embeeding_object.query,
        #     "ncm_code": embeeding_object.ncm_code,
        #     "product-description": embeeding_object.description,
        # },
    })