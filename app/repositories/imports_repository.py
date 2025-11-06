# Third-party imports
from typing import List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func, update
# Local imports
from app.model.imports import Imports
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.imports import ImportCreate, ImportUpdate
from app.model.supplier_product import SupplierProduct
from app.model.order import Order


class ImportsRepository(RepositoryInterface[ImportCreate, ImportUpdate, Imports]):
    def __init__(self, db_session: AsyncSession, model: Type[Imports]):
        self._db_session = db_session
        self._model = model

    async def save(self, import_data) -> Imports:
        """Create a new import record in the database."""
        imports_dict = import_data.model_dump()

        new_import = self._model(**imports_dict)

        try:
            self._db_session.add(new_import)
            await self._db_session.commit()
            await self._db_session.refresh(new_import)
            return new_import
        except SQLAlchemyError as e:
            await self._db_session.rollback()
            raise e

    async def list_all(self) -> List[Imports]:
      subq = select(func.max(Order.order_date)).scalar_subquery()
      stmt = (
        select(Imports)  
        .join(Imports.order) 
        .options(
            joinedload(Imports.manufacturer), 
            joinedload(Imports.supplier_product).joinedload(SupplierProduct.supplier),  
            joinedload(Imports.supplier_product).joinedload(SupplierProduct.product),  
            joinedload(Imports.order),  
        )
        .where(Order.order_date == subq)  
    )

      result = await self._db_session.execute(stmt) 
      return result.scalars().all()

    async def get_by_id(self, obj_id: int) -> Optional[Imports]:
        pass

    async def update(self, obj_id:int, obj_data: ImportUpdate) -> Imports:
      stmt = (
        update(self._model)
        .where(self._model.id == obj_id)
        .values(**obj_data.model_dump(exclude_unset=True))
        .returning(self._model)
      )
      result = await self._db_session.execute(stmt)
      return result.scalars().first()

    async def delete(self, obj_id: int) -> None:
        pass
    