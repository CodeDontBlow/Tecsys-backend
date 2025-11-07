from typing import List, Type
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select

from app.model.manufacturer import Manufacturer
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.manufacturer import ManufacturerCreate, ManufacturerUpdate


class ManufacturerRepository(
    RepositoryInterface[ManufacturerCreate, ManufacturerUpdate, Manufacturer]
):
    def __init__(self, db_session: AsyncSession, model: Type[Manufacturer]):
        self.db_session = db_session
        self.model = model

    async def save(self, obj_data: ManufacturerCreate) -> Manufacturer:
        manufacturer_dict = obj_data.model_dump()

        new_manufacturer = Manufacturer(**manufacturer_dict)

        try:
            self.db_session.add(new_manufacturer)
            await self.db_session.commit()
            await self.db_session.refresh(new_manufacturer)
            return new_manufacturer
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def list_all(self) -> List[Manufacturer]:
        """List all manufacturers."""
        stmt = select(self.model)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, obj_id: int) -> Manufacturer:
        pass

    async def update(self, obj_id: int, obj_data: ManufacturerUpdate) -> Manufacturer:
        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**obj_data.model_dump(exclude_unset=True))
            .returning(self.model)
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def delete(self, obj_id: int) -> None:
        pass
