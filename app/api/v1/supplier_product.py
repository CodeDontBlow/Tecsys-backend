from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.supplier_product import SupplierProduct
from app.schemas.supplier_product import SupplierProductUpdate

router = APIRouter(prefix="/supplierproduct")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SupplierProduct).order_by(asc(SupplierProduct.id)))
    items = result.scalars().all()
    if not items:
        raise HTTPException(status_code=404, detail="No supplier products found.")
    return items


@router.put("/{id}", response_model=SupplierProductUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, supplier_product_update: SupplierProductUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SupplierProduct).where(SupplierProduct.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Supplier product not found.")

    update_data = supplier_product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SupplierProduct).where(SupplierProduct.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="SupplierProduct not found.")
    await db.delete(item)
    await db.commit()
    return {"message": "SupplierProduct deleted successfully."}