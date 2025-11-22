from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_session
from app.model.supplier import Supplier
from app.schemas.supplier import SupplierUpdate
from app.repositories.supplier_repository import SupplierRepository
from app.log.logger import logger  


router = APIRouter(prefix="/supplier")

@router.put("/{id}", response_model=SupplierUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, supplier_update: SupplierUpdate, db: AsyncSession = Depends(get_session)):
    logger.info(f"[SUPPLIER] PUT /supplier/{id}")
    repo = SupplierRepository(db, Supplier)
    try:
        updated = await repo.update(id, supplier_update)
        if not updated:
            logger.warning(f"[SUPPLIER] Supplier with id={id} not found.")
            raise HTTPException(status_code=404, detail="Supplier not found.")
        logger.info(f"[SUPPLIER] Supplier with id={id} updated successfully.")
        return updated
    except Exception as e:
        logger.error(f"[SUPPLIER] Error in PUT /supplier/{id}: {e}")
        raise


# @router.delete("/{id}", status_code=status.HTTP_200_OK)
# async def delete(id: int, db: AsyncSession = Depends(get_session)):
#     logger.info(f"[SUPPLIER] DELETE /supplier/{id}")
#     try:
#         result = await db.execute(select(Supplier).where(Supplier.id == id))
#         item = result.scalars().first()
#         if not item:
#             logger.warning(f"[SUPPLIER] Supplier with id={id} not found.")
#             raise HTTPException(status_code=404, detail="Supplier not found.")

#         await db.delete(item)
#         await db.commit()
#         logger.info(f"[SUPPLIER] Supplier with id={id} deleted successfully.")
#         return {"message": "Supplier deleted successfully."}
#     except Exception as e:
#         logger.error(f"[SUPPLIER] Error in DELETE /supplier/{id}: {e}")
#         raise