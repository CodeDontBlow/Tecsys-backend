# Third-party imports
from typing import List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

# Local imports
from app.model.imports import Imports
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.imports import ImportCreate, ImportUpdate


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
        pass

    async def get_by_id(self, obj_id: int) -> Optional[Imports]:
        pass

    async def update(self, obj_data: ImportUpdate) -> Imports:
        pass

    async def delete(self, obj_id: int) -> None:
        pass
