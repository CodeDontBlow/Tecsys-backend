from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.model.imports import Imports
from app.schemas.imports import ImportResponse, ImportUpdate, ImportUpdateResponse
from app.log.logger import logger
from app.repositories.imports_repository import ImportsRepository

router = APIRouter(prefix="/imports")

@router.get("/", response_model=List[ImportResponse], status_code=status.HTTP_200_OK)
async def list_all(
    order_id: int | None = Query(None),
    db: AsyncSession = Depends(get_session)
):
    logger.info("[IMPORTS] GET /imports")

    try:
        repo = ImportsRepository(db, Imports)

        items = (
            await repo.list_by_order_id(order_id)
            if order_id is not None
            else await repo.list_all()
        )
        if not items:
            raise HTTPException(status_code=404, detail="No imports found.")
        return items
    except Exception as e:
        logger.error(f"[IMPORTS] Error in GET /imports: {e}")
        raise

@router.put("/{id}", response_model=ImportUpdateResponse, status_code=status.HTTP_200_OK)
async def replace(id: int, import_update: ImportUpdate, db: AsyncSession = Depends(get_session)):
    logger.info(f"[IMPORTS] PUT /imports/{id}")
    try:
        repo = ImportsRepository(db, Imports)
        item = await repo.update(id, import_update)
        if not item:
            logger.warning(f"[IMPORTS] Import with id={id} not found.")
            raise HTTPException(status_code=404, detail="Import not found.")
        logger.info(f"[IMPORTS] Import with id={id} updated successfully.")
        return ImportUpdateResponse.model_validate(item, from_attributes=True)
    except Exception as e:
        logger.error(f"[IMPORTS] Error in PUT /imports/{id}: {e}")
        raise

@router.delete("/order/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_order_id(order_id: int, db: AsyncSession = Depends(get_session)):
    logger.info(f"[IMPORTS] DELETE BY ORDER ID /imports/{order_id}")
    try:
        repo = ImportsRepository(db, Imports)
        await repo.delete_by_order_id(order_id)
        logger.info(f"[IMPORTS] Imports with order_id={order_id} deleted successfully.")
    except Exception as e:
        logger.error(f"[IMPORTS] Error in DELETE BY ORDER ID /imports/{order_id}: {e}")
        raise 