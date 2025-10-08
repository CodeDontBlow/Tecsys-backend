from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from fastapi import HTTPException
from app.model.supplyer_product import SupplyerProduct
from app.schemas.supplyer_product import SupplierProductUpdate

async def findById(db: AsyncSession, id: int):
    result = await db.execute(select(SupplyerProduct).where(SupplyerProduct.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Supplyer Product with id {id} not found")
    return item

async def listAll(db: AsyncSession):
    result = await db.execute(select(SupplyerProduct).order_by(asc(SupplyerProduct.id)))
    return result.scalars().all()

async def replace(db: AsyncSession, id:int, data: SupplierProductUpdate):
    item = await findById(db, id)
    item.erp_description = data.erp_description
    await db.commit()
    await db.refresh(item)
    return item