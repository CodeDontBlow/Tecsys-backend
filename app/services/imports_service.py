from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from fastapi import HTTPException
from app.model.imports import Imports
from app.schemas.imports import ImportUpdate

async def findById(db: AsyncSession, id: int):
    result = await db.execute(select(Imports).where(Imports.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Import with id {id} not found")
    return item

async def listAll(db: AsyncSession):
    result = await db.execute(select(Imports).order_by(asc(Imports.id)))
    return result.scalars().all()

async def replace(db: AsyncSession, id: int, data: ImportUpdate):
    item = await findById(db, id)
    item.product_part_number = data.product_part_number
    await db.commit()
    await db.refresh(item)
    return item