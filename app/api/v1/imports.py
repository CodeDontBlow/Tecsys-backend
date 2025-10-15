from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from app.db.database import get_session
from app.model.imports import Imports
from app.schemas.imports import ImportUpdate

router = APIRouter(prefix="/imports")


@router.get("/",status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Imports).order_by(asc(Imports.id)))
    items = result.scalars().all()
    if not items:
        raise HTTPException(status_code=404, detail="No imports found.")
    return items


@router.put("/{id}", response_model=ImportUpdate, status_code=status.HTTP_200_OK)
async def replace(id: int, import_update: ImportUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Imports).where(Imports.id == id))
    item = result.scalars().first()

    if not item:
          raise HTTPException(status_code=404, detail="Import not found.")

    update_data = import_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item
    

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Imports).where(Imports.id == id))
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail="Import not found.")

    await db.delete(item)
    await db.commit()

    return {"message": "Import deleted successfully."}
    
