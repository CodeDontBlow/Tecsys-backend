from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.model.manufacturer import Manufacturer
from app.schemas.manufacturer import ManufacturerUpdate, ManufacturerResponse
from app.log.logger import logger
from app.repositories.manufacturer_repository import ManufacturerRepository

router = APIRouter(prefix="/manufacturer")

@router.get("/", response_model=List[ManufacturerResponse], status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    logger.info("[MANUFACTURER] GET /manufacturer")
    try:
        repo = ManufacturerRepository(db, Manufacturer)
        items = await repo.list_all()
        if not items:
            logger.warning("[MANUFACTURER] No manufacturers found.")
            raise HTTPException(status_code=404, detail="No manufacturers found.")
        logger.info(f"[MANUFACTURER] Returned {len(items)} manufacturers.")
        return items
    except Exception as e:
        logger.error(f"[MANUFACTURER] Error in GET /manufacturer: {e}")
        raise


@router.put("/{id}", response_model=ManufacturerResponse, status_code=status.HTTP_200_OK)
async def replace(id: int, manufacturer_update: ManufacturerUpdate, db: AsyncSession = Depends(get_session)):
    logger.info(f"[MANUFACTURER] PUT /manufacturer/{id}")
    try:
        repo = ManufacturerRepository(db, Manufacturer)
        item = await repo.update(id, manufacturer_update)
        if not item:
            logger.warning(f"[MANUFACTURER] Manufacturer with id={id} not found.")
            raise HTTPException(status_code=404, detail="Manufacturer not found.")
        logger.info(f"[MANUFACTURER] Manufacturer with id={id} updated successfully.")
        return item
    except Exception as e:
        logger.error(f"[MANUFACTURER] Error in PUT /manufacturer/{id}: {e}")
        raise


# @router.delete("/{id}", status_code=status.HTTP_200_OK)
# async def delete(id: int, db: AsyncSession = Depends(get_session)):
#     logger.info(f"[MANUFACTURER] DELETE /manufacturer/{id}")
#     try:
#         result = await db.execute(select(Manufacturer).where(Manufacturer.id == id))
#         item = result.scalars().first()
#         if not item:
#             logger.warning(f"[MANUFACTURER] Manufacturer with id={id} not found.")
#             raise HTTPException(status_code=404, detail="Manufacturer not found.")

#         await db.delete(item)
#         await db.commit()
#         logger.info(f"[MANUFACTURER] Manufacturer with id={id} deleted successfully.")
#         return {"message": "Manufacturer deleted successfully."}
#     except Exception as e:
#         logger.error(f"[MANUFACTURER] Error in DELETE /manufacturer/{id}: {e}")
#         raise
