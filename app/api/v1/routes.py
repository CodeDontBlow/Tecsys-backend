from fastapi import APIRouter
from .pdf import api_router as pdf_router
from .imports import api_router as imports_router
from .manufacturer import api_router as manufacturer_router
from .order import api_router as order_router
from .product import api_router as product_router
from .supplier_product import api_router as supplier_product_router
from .supplier import api_router as supplier_router
from .ncm import api_router as ncm_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(pdf_router)
api_router.include_router(imports_router)
api_router.include_router(manufacturer_router)
api_router.include_router(order_router)
api_router.include_router(product_router)
api_router.include_router(supplier_product_router)
api_router.include_router(supplier_router)
api_router.include_router(ncm_router)
