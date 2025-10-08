from fastapi import APIRouter, status, Depends
from app.services import imports_service
from app.db.database import get_session
from app.schemas.imports import ImportUpdate
from sqlalchemy.ext.asyncio import AsyncSession


api_router = APIRouter(prefix="/imports")

@api_router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    return await imports_service.listAll(db)

@api_router.put("/{id}", status_code=status.HTTP_200_OK)
async def replace(id:int, data:ImportUpdate, db: AsyncSession = Depends(get_session)):
    return await imports_service.replace(db, id, data)

