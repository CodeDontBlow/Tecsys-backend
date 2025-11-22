from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.model.product import Product
from app.schemas.product import ProductUpdate, ProductResponse
from app.log.logger import logger  
from app.repositories.product_repository import ProductRepository

router = APIRouter(prefix="/product")

@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    logger.info("[PRODUCT] GET /product")
    try:
        repo = ProductRepository(db, Product)
        items = await repo.list_all()
        if not items:
            logger.warning("[PRODUCT] No products found.")
            raise HTTPException(status_code=404, detail="No products found.")
        logger.info(f"[PRODUCT] Returned {len(items)} products")
        return items
    except Exception as e:
        logger.error(f"[PRODUCT] Error in GET /product: {e}")
        raise

@router.put("/{id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def replace(id: int, product_update: ProductUpdate, db: AsyncSession = Depends(get_session)):
    logger.info(f"[PRODUCT] PUT /product/{id}")
    try:
        repo = ProductRepository(db, Product)
        item = await repo.update(id, product_update)
        if not item:
            logger.warning(f"[PRODUCT] Product with id={id} not found.")
            raise HTTPException(status_code=404, detail="Product not found.")
        logger.info(f"[PRODUCT] Product with id={id} updated successfully.")
        return item
    except Exception as e:
        logger.error(f"[PRODUCT] Error in PUT /product/{id}: {e}")
        raise

# @router.delete("/{id}", status_code=status.HTTP_200_OK)
# async def delete(id: int, db: AsyncSession = Depends(get_session)):
#     logger.info(f"[PRODUCT] DELETE /product/{id}")
#     try:
#         result = await db.execute(select(Product).where(Product.id == id))
#         item = result.scalars().first()
#         if not item:
#             logger.warning(f"[PRODUCT] Product with id={id} not found.")
#             raise HTTPException(status_code=404, detail="Product not found.")

#         await db.delete(item)
#         await db.commit()
#         logger.info(f"[PRODUCT] Product with id={id} deleted successfully.")
#         return {"message": "Product deleted successfully."}
#     except Exception as e:
#         logger.error(f"[PRODUCT] Error in DELETE /product/{id}: {e}")
#         raise