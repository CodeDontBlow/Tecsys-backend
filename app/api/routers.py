from fastapi import APIRouter

from app.api.controllers.product_router import router as product_router
from app.api.controllers.manufacturer_router import router as manufacturer_router
from app.api.controllers.supplyer_router import router as supplyer_router

api_router = APIRouter()

api_router.include_router(product_router, prefix="/products", tags=["products"])
api_router.include_router(manufacturer_router, prefix="/manufacturer", tags=["manufacturer"])
api_router.include_router(supplyer_router, prefix="/supplyer", tags=["supplyer"])
