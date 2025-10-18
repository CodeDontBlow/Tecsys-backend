# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Type

# Local imports
from app.model.supplier_product import SupplierProduct


class SupplierProductRepository:
    def __init__(self, db_session: AsyncSession, model: Type[SupplierProduct]):
        self.db_session = db_session
        self.model = model

    async def create(self, supplier_data) -> SupplierProduct:
        """
        Create a new supplier_product relationship record in the database.
        """
        supplier_product_dict = supplier_data.model_dump()

        new_supplier_product = SupplierProduct(**supplier_product_dict)

        try:
            self.db_session.add(new_supplier_product)
            await self.db_session.commit()
            await self.db_session.refresh(new_supplier_product)
            return new_supplier_product
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e
