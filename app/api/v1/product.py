from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.log.logger import logger  

router = APIRouter(prefix="/product")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    logger.info("[PRODUCT] GET /product")
    try:
        result = await db.execute(select(Product).order_by(asc(Product.id)))
        items = result.scalars().all()
        if not items:
            logger.warning("[PRODUCT] No products found.")
            raise HTTPException(status_code=404, detail="No products found.")
        logger.info(f"[PRODUCT] Returned {len(items)} products")
        return items
    except Exception as e:
        logger.error(f"[PRODUCT] Error in GET /product: {e}")
        raise


@router.post("/save", response_model=ProductCreate, status_code=status.HTTP_200_OK)
async def save(product_create: ProductCreate, db: AsyncSession = Depends(get_session)):
    try:
        pro_repo = ProductRepository(db, Product)
        new_product = await pro_repo.save(product_create)
        return new_product
    except Exception as e:
        logger.error(f"[PRODUCT] Error in post /product: {e}")
        raise


@router.put("/{id}", response_model=ProductUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, product_update: ProductUpdate, db: AsyncSession = Depends(get_session)):
    logger.info(f"[PRODUCT] PUT /product/{id}")
    try:
        result = await db.execute(select(Product).where(Product.id == id))
        item = result.scalars().first()
        if not item:
            logger.warning(f"[PRODUCT] Product with id={id} not found.")
            raise HTTPException(status_code=404, detail="Product not found.")

        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)

        await db.commit()
        await db.refresh(item)
        logger.info(f"[PRODUCT] Product with id={id} updated successfully.")
        return item
    except Exception as e:
        logger.error(f"[PRODUCT] Error in PUT /product/{id}: {e}")
        raise


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    logger.info(f"[PRODUCT] DELETE /product/{id}")
    try:
        result = await db.execute(select(Product).where(Product.id == id))
        item = result.scalars().first()
        if not item:
            logger.warning(f"[PRODUCT] Product with id={id} not found.")
            raise HTTPException(status_code=404, detail="Product not found.")

        await db.delete(item)
        await db.commit()
        logger.info(f"[PRODUCT] Product with id={id} deleted successfully.")
        return {"message": "Product deleted successfully."}
    except Exception as e:
        logger.error(f"[PRODUCT] Error in DELETE /product/{id}: {e}")
        raise