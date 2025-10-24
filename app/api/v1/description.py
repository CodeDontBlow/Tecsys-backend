from fastapi import APIRouter, HTTPException
from app.libs.final_description.generate_final_desc import Generate_final_desc
from app.log.logger import logger
from app.libs.websocket.manager import ws_manager
from app.libs.websocket.worker import enqueue_task

router = APIRouter(prefix="/description")

@router.get("/")
async def generator_description(
    supplier_desc: str = "AVNET ELECTRONIC MARKETING",
    erp_desc: str = "Diode Gen Purp 100V 150Ma Sod123 Rohs Compliant: Yes |Micro Commercial Components 1N4148W-TP"
):
    logger.info("[DESCRIPTION] GET /description")
    try:
     
        await enqueue_task(lambda: ws_manager.send_json({"process": "description", "status": "in_progress"}))

        erp_dict = { "ITEM-001": erp_desc }
        result = await Generate_final_desc.generate_final_desc_async(erp_dict, supplier_desc)

        await enqueue_task(lambda: ws_manager.send_json({"process": "description", "status": "completed"}))
        await enqueue_task(lambda: ws_manager.send_json({"process": "check 2", "status": "completed"}))
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    