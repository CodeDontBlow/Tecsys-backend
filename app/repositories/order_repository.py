from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Type

from app.model.order import Order
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.order import OrderCreate, OrderUpdate


class OrderRepository(RepositoryInterface[OrderCreate, OrderUpdate, Order]):
    def __init__(self, db_session: AsyncSession, model: Type[Order]):
        self.db_session = db_session
        self.model = model

    async def save(self, obj_data: OrderCreate) -> Order:
        """Create a new supplier record in the database."""
        orrder_dict = obj_data.model_dump()

        new_product = Order(**orrder_dict)

        try:
            self.db_session.add(new_product)
            await self.db_session.commit()
            await self.db_session.refresh(new_product)
            return new_product
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def list_all(self) -> List[Order]:
        pass

    async def get_by_id(self, obj_id: int) -> Optional[Order]:
        pass

    async def update(self, obj_data: OrderUpdate) -> Order:
        pass

    async def delete(self, obj_id: int) -> None:
        pass
