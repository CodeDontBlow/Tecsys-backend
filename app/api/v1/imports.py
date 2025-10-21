from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.imports import Imports
from app.schemas.imports import ImportUpdate
from app.log.logger import logger

router = APIRouter(prefix="/imports")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    logger.info("[IMPORTS] GET /imports")
    try:
        result = await db.execute(select(Imports).order_by(asc(Imports.id)))
        items = result.scalars().all()
        if not items:
            logger.warning("[IMPORTS] No imports found.")
            raise HTTPException(status_code=404, detail="No imports found.")
        logger.info(f"[IMPORTS] Returned {len(items)} imports.")
        return items
    except Exception as e:
        logger.error(f"[IMPORTS] Error in GET /imports: {e}")
        raise


@router.put("/{id}", response_model=ImportUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, import_update: ImportUpdate, db: AsyncSession = Depends(get_session)):
    logger.info(f"[IMPORTS] PUT /imports/{id}")
    try:
        result = await db.execute(select(Imports).where(Imports.id == id))
        item = result.scalars().first()

        if not item:
            logger.warning(f"[IMPORTS] Import with id={id} not found.")
            raise HTTPException(status_code=404, detail="Import not found.")

        update_data = import_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)

        await db.commit()
        await db.refresh(item)
        logger.info(f"[IMPORTS] Import with id={id} updated successfully.")
        return item
    except Exception as e:
        logger.error(f"[IMPORTS] Error in PUT /imports/{id}: {e}")
        raise


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    logger.info(f"[IMPORTS] DELETE /imports/{id}")
    try:
        result = await db.execute(select(Imports).where(Imports.id == id))
        item = result.scalars().first()

        if not item:
            logger.warning(f"[IMPORTS] Import with id={id} not found.")
            raise HTTPException(status_code=404, detail="Import not found.")

        await db.delete(item)
        await db.commit()
        logger.info(f"[IMPORTS] Import with id={id} deleted successfully.")
        return {"message": "Import deleted successfully."}
    except Exception as e:
        logger.error(f"[IMPORTS] Error in DELETE /imports/{id}: {e}")
        raise