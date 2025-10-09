from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from fastapi import HTTPException
from app.model.supplier_product import SupplierProduct
from app.schemas.supplier_product import SupplierProductUpdate


async def findById(db: AsyncSession, id: int):
    result = await db.execute(select(SupplierProduct).where(SupplierProduct.id == id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(
            status_code=404, detail=f"Supplier Product with id {id} not found"
        )
    return item


async def listAll(db: AsyncSession):
    result = await db.execute(select(SupplierProduct).order_by(asc(SupplierProduct.id)))
    return result.scalars().all()


async def replace(db: AsyncSession, id: int, data: SupplierProductUpdate):
    item = await findById(db, id)
    item.erp_description = data.erp_description
    await db.commit()
    await db.refresh(item)
    return item
