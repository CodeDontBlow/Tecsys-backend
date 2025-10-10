from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from fastapi import HTTPException
from app.model.product import Product
from app.schemas.product import ProductUpdate

async def findById(db: AsyncSession, id: int):
    result = await db.execute(select(Product).where(Product.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    return item

async def listAll(db: AsyncSession):
    result = await db.execute(select(Product).order_by(asc(Product.id)))
    return result.scalars().all()

async def replace(db: AsyncSession, id:int, data: ProductUpdate):
    item = await findById(db, id)
    item.ncm = data.ncm
    item.final_description = data.final_description
    await db.commit()
    await db.refresh(item)
    return item