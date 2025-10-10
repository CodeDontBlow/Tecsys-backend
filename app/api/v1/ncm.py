from fastapi import APIRouter
from app.services.tipi_service import get_ncm

api_router = APIRouter(prefix="/ncm")


@api_router.get("/preview")
async def ncm_preview():
    mock = "LED Verde, 2 mm, 5,2 mcd, 560 nm, SMD, If 20 mA, Vf 2,1 V, Ângulo 130°, Lente Dome"
    result = get_ncm(mock)
    return result
