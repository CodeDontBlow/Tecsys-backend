from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.order import Order
from app.schemas.order import OrderUpdate

router = APIRouter(prefix="/order")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Order).order_by(asc(Order.id)))
    items = result.scalars().all()
    if not items:
        raise HTTPException(status_code=404, detail="No orders found.")
    return items


@router.put("/{id}", response_model=OrderUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, order_update: OrderUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Order).where(Order.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Order not found.")

    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Order).where(Order.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Order not found.")
    await db.delete(item)
    await db.commit()
    return {"message": "Order deleted successfully."}