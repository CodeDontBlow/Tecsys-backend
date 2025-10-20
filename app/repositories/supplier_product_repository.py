# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Type, List

# Local imports
from app.model.supplier_product import SupplierProduct
from app.schemas.supplier_product import SupplierProductCreate, SupplierProductUpdate
from app.repositories.repository_interface import RepositoryInterface


class SupplierProductRepository(
    RepositoryInterface[SupplierProductCreate, SupplierProductUpdate, SupplierProduct]
):
    def __init__(self, db_session: AsyncSession, model: Type[SupplierProduct]):
        self._db_session = db_session
        self.model = model

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
        pass

    async def get_by_id(self, obj_id: int) -> SupplierProduct:
        pass

    async def update(self, obj_data: SupplierProductUpdate) -> SupplierProduct:
        pass

    async def delete(self, obj_id: int) -> None:
        pass
