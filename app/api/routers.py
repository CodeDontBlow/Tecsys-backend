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
async def run_flow(pdf: UploadFile = File(...)):
    data = {}

    # pdf extraction process
    pdf_bytes = await pdf.read()
    pdf_file = EnterPDF(pdf_bytes=pdf_bytes)
    pdf_data = pdf_file.process_enter()
    
    # filter pdf_data
    test = ['mercadoria_01']
    filtered_pdf_data = {k: pdf_data[k] for k in test if k in pdf_data}

    # get products descriptions in filtered data
    products_descriptions = {k: filtered_pdf_data[k]['nome'] for k in filtered_pdf_data}

    # run llm decriptions generate
    final_product_description = await Generate_final_desc.generate_final_desc_async(products_descriptions)

    # get ncm by a descript
    embeeding_object= get_ncm("Capacitor eletrolítico de alumínio, 10 uF, 100 V, ±20%, 2000 horas a 85°C, Radial Can - SMD")

    # build json response
    for key, product_data in filtered_pdf_data.items():
        data[key] = {    
            'id': product_data['numero'], 
            'erp_code': product_data['codigo_erp'],
            'part_number': product_data['part_number'],
            'final_description': final_product_description[key],
            'product_embeeding': embeeding_object
            }

    print(final_product_description)
    print(embeeding_object)

    return JSONResponse(content={"data": data})