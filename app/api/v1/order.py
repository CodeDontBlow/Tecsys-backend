from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.order import Order
from app.schemas.order import OrderUpdate
from app.log.logger import logger  

router = APIRouter(prefix="/order")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    logger.info("[ORDER] GET /order")
    try:
        result = await db.execute(select(Order).order_by(asc(Order.id)))
        items = result.scalars().all()
        if not items:
            logger.warning("[ORDER] No orders found.")
            raise HTTPException(status_code=404, detail="No orders found.")
        logger.info(f"[ORDER] Returned {len(items)} orders")
        return items
    except Exception as e:
        logger.error(f"[ORDER] Error in GET /order: {e}")
        raise


@router.put("/{id}", response_model=OrderUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, order_update: OrderUpdate, db: AsyncSession = Depends(get_session)):
    logger.info(f"[ORDER] PUT /order/{id}")
    try:
        result = await db.execute(select(Order).where(Order.id == id))
        item = result.scalars().first()
        if not item:
            logger.warning(f"[ORDER] Order with id={id} not found.")
            raise HTTPException(status_code=404, detail="Order not found.")

        update_data = order_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)

        await db.commit()
        await db.refresh(item)
        logger.info(f"[ORDER] Order with id={id} updated successfully.")
        return item
    except Exception as e:
        logger.error(f"[ORDER] Error in PUT /order/{id}: {e}")
        raise


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    logger.info(f"[ORDER] DELETE /order/{id}")
    try:
        result = await db.execute(select(Order).where(Order.id == id))
        item = result.scalars().first()
        if not item:
            logger.warning(f"[ORDER] Order with id={id} not found.")
            raise HTTPException(status_code=404, detail="Order not found.")

        await db.delete(item)
        await db.commit()
        logger.info(f"[ORDER] Order with id={id} deleted successfully.")
        return {"message": "Order deleted successfully."}
    except Exception as e:
        logger.error(f"[ORDER] Error in DELETE /order/{id}: {e}")
        raise