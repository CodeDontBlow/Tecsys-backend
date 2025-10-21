from fastapi import APIRouter, HTTPException
from app.services import ncm_service
from app.log.logger import logger

router = APIRouter(prefix="/ncm")


@router.get("/")
async def search_ncm(query: str = "LED Verde, 2 mm, 5,2 mcd, 560 nm, SMD, If 20 mA, Vf 2,1 V, Ângulo 130°, Lente Dome"):
    logger.info("[NCM] GET /ncm")
    logger.info(f"[NCM] Query received: {query}")
    try:
        return ncm_service.get_ncm(query)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))