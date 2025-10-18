from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.manufacturer import Manufacturer
from app.schemas.manufacturer import ManufacturerUpdate

router = APIRouter(prefix="/manufacturer")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Manufacturer).order_by(asc(Manufacturer.id)))
    items = result.scalars().all()
    if not items:
        raise HTTPException(status_code=404, detail="No manufacturers found.")
    return items


@router.put("/{id}", response_model=ManufacturerUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, manufacturer_update: ManufacturerUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Manufacturer).where(Manufacturer.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")

    update_data = manufacturer_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Manufacturer).where(Manufacturer.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")
    await db.delete(item)
    await db.commit()
    return {"message": "Manufacturer deleted successfully."}
