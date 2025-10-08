from fastapi import APIRouter, status, Depends
from app.services import supplier_service
from app.db.database import get_session
from app.schemas.supplyer import SupplierUpdate
from sqlalchemy.ext.asyncio import AsyncSession

api_router = APIRouter(prefix="/supplier")

@api_router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    return await supplier_service.listAll(db)

@api_router.put("/{id}", status_code=status.HTTP_200_OK)
async def replace(data:SupplierUpdate, id:int, db: AsyncSession = Depends(get_session)):
    return await supplier_service.replace(db, id, data)

