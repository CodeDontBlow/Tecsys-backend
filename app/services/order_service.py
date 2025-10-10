from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from fastapi import HTTPException
from app.model.order import Order
from app.schemas.order import OrderUpdate
from datetime import datetime, date

async def findById(db: AsyncSession, id: int):
    result = await db.execute(select(Order).where(Order.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
    return item

async def listAll(db: AsyncSession):
    result = await db.execute(select(Order).order_by(asc(Order.id)))
    return result.scalars().all()

async def replace(db: AsyncSession,id:int, data: OrderUpdate):
    item = await findById(db, id)
    if isinstance(data.order_date, str):
        if isinstance(data.order_date, str):
            item.order_date = datetime.strptime(data.order_date, "%Y-%m-%d").date()
        else:
            item.order_date = data.order_date         
    await db.commit()
    await db.refresh(item)
    return item