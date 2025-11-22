# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, select
from typing import Type, Optional, List

# Local imports
from app.model.product import Product
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository(RepositoryInterface[ProductCreate, ProductUpdate, Product]):
    def __init__(self, db_session: AsyncSession, model: Type[Product]):
        self._db_session = db_session
        self.model = model

    async def save(self, obj_data: ProductCreate) -> Product:
        """Create a new supplier record in the database."""
        product_dict = obj_data.model_dump()

        new_product = Product(**product_dict)

        try:
            self._db_session.add(new_product)
            await self._db_session.commit()
            await self._db_session.refresh(new_product)
            return new_product
        except SQLAlchemyError as e:
            await self._db_session.rollback()
            raise e

    async def list_all(self) -> List[Product]:
        stmt = select(self.model)
        result = await self._db_session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, obj_id: int) -> Optional[Product]:
        pass

    async def update(self, obj_id: int, obj_data: ProductUpdate) -> Product:
        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**obj_data.model_dump(exclude_unset=True))
            .returning(self.model)
        )
        result = await self._db_session.execute(stmt)
        updated = result.scalars().first()
        if updated is None:
            return None
        await self._db_session.commit()
        await self._db_session.refresh(updated)
        return updated

    async def delete(self, obj_id: int) -> None:
        pass
