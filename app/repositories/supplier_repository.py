# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, Optional, List
from sqlalchemy.exc import SQLAlchemyError

# Local imports
from app.model.supplier import Supplier
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierRepository(RepositoryInterface[SupplierCreate, SupplierUpdate, Supplier]):
    def __init__(self, db_session: AsyncSession, model: Type[Supplier]):
        self._db_session = db_session
        self.model = model

    async def save(self, obj_data: SupplierCreate) -> Supplier:
        """Create a new supplier record in the database."""
        supplier_dict = obj_data.model_dump()

        new_supplier = Supplier(**supplier_dict)

        try:
            self._db_session.add(new_supplier)
            await self._db_session.commit()
            await self._db_session.refresh(new_supplier)
            return new_supplier
        except SQLAlchemyError as e:
            await self._db_session.rollback()
            raise e

    async def list_all(self) -> List[Supplier]:
        pass

    async def get_by_id(self, obj_id: int) -> Optional[Supplier]:
        pass

    async def update(self, obj_data: SupplierUpdate) -> Supplier:
        pass

    async def delete(self, obj_id: int) -> None:
        pass
