from fastapi import APIRouter, HTTPException
from app.libs.ncm import setup
from app.log.logger import logger
from app.libs.websocket.manager import ws_manager
from app.libs.websocket.worker import enqueue_task


router = APIRouter(prefix="/ncm")

@router.get("/")
async def search_ncm(query: str = "LED Verde, 2 mm SMD"):
    logger.info(f"[NCM] GET /ncm - Query: {query}")
    try:

        await enqueue_task(lambda: ws_manager.send_json({"process": "ncm", "status": "in_progress"}))

        results = await setup.get_ncm(query)
        
        await enqueue_task(lambda: ws_manager.send_json({"process": "ncm", "status": "completed"}))

        return results

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))