from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.supplier import Supplier
from app.schemas.supplier import SupplierUpdate

router = APIRouter(prefix="/supplier")


@router.get("/", response_model=list[SupplierUpdate], status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Supplier).order_by(asc(Supplier.id)))
    items = result.scalars().all()
    if not items:
        raise HTTPException(status_code=404, detail="No suppliers found.")
    return items


@router.put("/{id}", response_model=SupplierUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, supplier_update: SupplierUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Supplier).where(Supplier.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Supplier not found.")

    update_data = supplier_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Supplier).where(Supplier.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Supplier not found.")
    await db.delete(item)
    await db.commit()
    return {"message": "Supplier deleted successfully."}