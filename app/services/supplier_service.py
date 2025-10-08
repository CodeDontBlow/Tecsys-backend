from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from fastapi import HTTPException
from app.model.supplyer import Supplyer
from app.schemas.supplyer import SupplierUpdate

async def findById(db: AsyncSession, id: int):
    result = await db.execute(select(Supplyer).where(Supplyer.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Supplier with id {id} not found")
    return item

async def listAll(db: AsyncSession):
    result = await db.execute(select(Supplyer).order_by(asc(Supplyer.id)))
    return result.scalars().all()

async def replace(db: AsyncSession, id:int, data: SupplierUpdate):
    item = await findById(db, id)
    item.name = data.name
    item.part_number = data.part_number
    await db.commit()
    await db.refresh(item)
    return item