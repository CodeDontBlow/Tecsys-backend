from fastapi import APIRouter, status, Depends
from app.services import product_service
from app.db.database import get_session
from app.schemas.product import ProductUpdate
from sqlalchemy.ext.asyncio import AsyncSession


api_router = APIRouter(prefix="/product")


@api_router.get("/", status_code=status.HTTP_200_OK)
async def list_all(db: AsyncSession = Depends(get_session)):
    return await product_service.listAll(db)


@api_router.put("/{id}", status_code=status.HTTP_200_OK)
async def replace(
    data: ProductUpdate, id: int, db: AsyncSession = Depends(get_session)
):
    return await product_service.replace(db, id, data)
