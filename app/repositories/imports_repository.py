# Third-party imports
from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

# Local imports
from app.model.imports import Imports


class ImportsRepository:
    def __init__(self, db_session: AsyncSession, model: Type[Imports]):
        self.db_session = db_session
        self.model = model

    async def save(self, import_data) -> Imports:
        """Create a new import record in the database."""
        imports_dict = import_data.model_dump()

        new_import = self.model(**imports_dict)

        try:
            self.db_session.add(new_import)
            await self.db_session.commit()
            await self.db_session.refresh(new_import)
            return new_import
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e
