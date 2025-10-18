# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Type, Optional, List

# Local imports
from app.model.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, db_session: AsyncSession, model: Type[Product]):
        self.db_session = db_session
        self.model = model

    async def save(self, obj_data: ProductCreate) -> Product:
        """Create a new supplier record in the database."""
        product_dict = obj_data.model_dump()

        new_product = Product(**product_dict)

        try:
            self.db_session.add(new_product)
            await self.db_session.commit()
            await self.db_session.refresh(new_product)
            return new_product
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def list_all(self) -> List[Product]:
        pass

    async def get_by_id(self, obj_id: int) -> Optional[Product]:
        pass

    async def update(self, obj_data: ProductUpdate) -> Product:
        pass

    async def delete(self, obj_id: int) -> None:
        pass
