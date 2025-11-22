from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.model.supplier_product import SupplierProduct
from app.schemas.supplier_product import SupplierProductUpdate, SupplierProductResponse, SupplierProductUpdateResponse
from app.log.logger import logger  
from app.repositories.supplier_product_repository import SupplierProductRepository

router = APIRouter(prefix="/supplierproduct")

@router.get("/", response_model=list[SupplierProductResponse], status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    logger.info("[SUPPLIERPRODUCT] GET /supplierproduct")
    try:
        repo = SupplierProductRepository(db, SupplierProduct)
        items = await repo.list_all()
        if not items:
            logger.warning("[SUPPLIERPRODUCT] No supplier products found.")
            raise HTTPException(status_code=404, detail="No supplier products found.")
        logger.info(f"[SUPPLIERPRODUCT] Returned {len(items)} supplier products")
        return items
    except Exception as e:
        logger.error(f"[SUPPLIERPRODUCT] Error in GET /supplierproduct: {e}")
        raise


@router.put("/{id}", response_model=SupplierProductUpdateResponse, status_code=status.HTTP_200_OK)
async def replace(id: int, supplier_product_update: SupplierProductUpdate, db: AsyncSession = Depends(get_session)):
    logger.info(f"[SUPPLIERPRODUCT] PUT /supplierproduct/{id}")
    try:
        repo = SupplierProductRepository(db, SupplierProduct)
        item = await repo.update(id, supplier_product_update)
        if not item:
            logger.warning(f"[SUPPLIERPRODUCT] SupplierProduct with id={id} not found.")
            raise HTTPException(status_code=404, detail="Supplier product not found.")
        logger.info(f"[SUPPLIERPRODUCT] SupplierProduct with id={id} updated successfully.")
        return item
    except Exception as e:
        logger.error(f"[SUPPLIERPRODUCT] Error in PUT /supplierproduct/{id}: {e}")
        raise

# @router.delete("/{id}", status_code=status.HTTP_200_OK)
# async def delete(id: int, db: AsyncSession = Depends(get_session)):
#     logger.info(f"[SUPPLIERPRODUCT] DELETE /supplierproduct/{id}")
#     try:
#         result = await db.execute(select(SupplierProduct).where(SupplierProduct.id == id))
#         item = result.scalars().first()
#         if not item:
#             logger.warning(f"[SUPPLIERPRODUCT] SupplierProduct with id={id} not found.")
#             raise HTTPException(status_code=404, detail="SupplierProduct not found.")

#         await db.delete(item)
#         await db.commit()
#         logger.info(f"[SUPPLIERPRODUCT] SupplierProduct with id={id} deleted successfully.")
#         return {"message": "SupplierProduct deleted successfully."}
#     except Exception as e:
#         logger.error(f"[SUPPLIERPRODUCT] Error in DELETE /supplierproduct/{id}: {e}")
#         raise