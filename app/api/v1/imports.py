from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_session
from app.model.imports import Imports
from app.model.supplier_product import SupplierProduct
from app.model.order import Order
from app.repositories.imports_repository import ImportsRepository
from app.schemas.imports import ImportCreate, ImportResponse, ImportUpdate
from app.log.logger import logger
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/imports")


@router.get(
    "/all-results", response_model=List[ImportResponse], status_code=status.HTTP_200_OK
)
async def list_all(db: AsyncSession = Depends(get_session)):
    subq = select(func.max(Order.order_date)).scalar_subquery()
    logger.info("[IMPORTS] GET /imports")
    try:
        stmt = (
            select(Imports)
            .join(Imports.order)
            .options(
                joinedload(Imports.manufacturer),
                joinedload(Imports.supplier_product).joinedload(
                    SupplierProduct.supplier
                ),
                joinedload(Imports.supplier_product).joinedload(
                    SupplierProduct.product
                ),
                joinedload(Imports.order),
            )
            .where(Order.order_date == subq)
        )

        result = await db.execute(stmt)
        items = result.scalars().all()
        if not items:
            logger.warning("[IMPORTS] No imports found.")
            raise HTTPException(status_code=404, detail="No imports found.")

        logger.info(f"[IMPORTS] Returned {len(items)} imports.")
        return items
    except Exception as e:
        logger.error(f"[IMPORTS] Error in GET /imports: {e}")
        raise


@router.post("/save", response_model=ImportCreate, status_code=status.HTTP_200_OK)
async def save(import_create: ImportCreate, db: AsyncSession = Depends(get_session)):
    try:
        pro_repo = ImportsRepository(db, Imports)
        new_import = await pro_repo.save(import_create)
        return new_import
    except Exception as e:
        logger.error(f"[SUPPLIER_PRODUCT] Error in post /supplierproduct: {e}")
        raise


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_normal(db: AsyncSession = Depends(get_session)):
    logger.info("[IMPORTS] GET /imports (ALL NORMAL - no joins)")

    try:
        stmt = select(Imports).order_by(Imports.id.asc())
        result = await db.execute(stmt)
        items = result.scalars().all()

        if not items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No imports found."
            )

        return items

    except Exception as e:
        logger.error(f"[IMPORTS] Error in GET /imports: {e}")
        raise


@router.put("/{id}", response_model=ImportUpdate, status_code=status.HTTP_200_OK)
async def replace(
    id: int, import_update: ImportUpdate, db: AsyncSession = Depends(get_session)
):
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
