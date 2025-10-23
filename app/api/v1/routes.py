from fastapi import APIRouter
from .pdf import router as pdf_router
from .imports import router as imports_router
from .manufacturer import router as manufacturer_router
from .order import router as order_router
from .product import router as product_router
from .supplier_product import router as supplier_product_router
from .supplier import router as supplier_router
from .ncm import router as ncm_router
from .ws import router as ws_router
from .description import router as description_router

router = APIRouter(prefix="/v1")
router.include_router(pdf_router)
router.include_router(imports_router)
router.include_router(manufacturer_router)
router.include_router(order_router)
router.include_router(product_router)
router.include_router(supplier_product_router)
router.include_router(supplier_router)
router.include_router(ncm_router)
router.include_router(ws_router)
router.include_router(description_router)
