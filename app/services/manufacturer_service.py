from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from fastapi import HTTPException
from app.model.manufacturer import Manufacturer
from app.schemas.manufacturer import ManufacturerUpdate

async def findById(db: AsyncSession, id: int):
    result = await db.execute(select(Manufacturer).where(Manufacturer.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Manufacturer with id {id} not found")
    return item

async def listAll(db: AsyncSession):
    result = await db.execute(select(Manufacturer).order_by(asc(Manufacturer.id)))
    return result.scalars().all()

async def replace(db: AsyncSession, id:int, data: ManufacturerUpdate):
    item = await findById(db, id)
    item.name = data.name
    item.address = data.address
    item.origin_country = data.origin_country
    await db.commit()
    await db.refresh(item)
    return item
