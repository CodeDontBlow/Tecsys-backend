from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.product import Product
from app.schemas.product import ProductUpdate

router = APIRouter(prefix="/product")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Product).order_by(asc(Product.id)))
    items = result.scalars().all()
    if not items:
        raise HTTPException(status_code=404, detail="No products found.")
    return items


@router.put("/{id}", response_model=ProductUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, product_update: ProductUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Product).where(Product.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found.")

    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Product).where(Product.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found.")
    await db.delete(item)
    await db.commit()
    return {"message": "Product deleted successfully."}