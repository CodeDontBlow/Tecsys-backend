# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, select
from sqlalchemy.orm import joinedload
from typing import Type, List

# Local imports
from app.model.supplier_product import SupplierProduct
from app.schemas.supplier_product import SupplierProductCreate, SupplierProductUpdate
from app.repositories.repository_interface import RepositoryInterface


class SupplierProductRepository(
    RepositoryInterface[SupplierProductCreate, SupplierProductUpdate, SupplierProduct]
):
    def __init__(self, db_session: AsyncSession, model: Type[SupplierProduct]):
        self._db_session = db_session
        self._model = model

    async def save(self, obj_data) -> SupplierProduct:
        """
        Create a new supplier_product relationship record in the database.
        """
        supplier_product_dict = obj_data.model_dump()

        new_supplier_product = SupplierProduct(**supplier_product_dict)

        try:
            self._db_session.add(new_supplier_product)
            await self._db_session.commit()
            await self._db_session.refresh(new_supplier_product)
            return new_supplier_product
        except SQLAlchemyError as e:
            await self._db_session.rollback()
            raise e

    async def list_all(self) -> List[SupplierProduct]:
        stmt = (
            select(SupplierProduct)
            .options(
                joinedload(SupplierProduct.supplier),          
                joinedload(SupplierProduct.product),           
            )
        )

        result = await self._db_session.execute(stmt)
        return result.scalars().unique().all()


    async def get_by_id(self, obj_id: int) -> SupplierProduct:
        pass

    async def update(self, obj_id: int, obj_data: SupplierProductUpdate) -> SupplierProduct:
        stmt = (
            update(self._model)
            .where(self._model.id == obj_id)
            .values(**obj_data.model_dump(exclude_unset=True))
            .returning(self._model)
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
