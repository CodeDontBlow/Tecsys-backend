from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.imports import Imports


class ImportsRepository:
    def __init__(self, db_session: AsyncSession, model: Type[Imports]):
        self.db_session = db_session
        self.model = model

    async def create(self, import_data) -> Imports:
        imports_dict = import_data.model_dump()

        new_import = self.model(**imports_dict)

        try:
            self.db_session.add(new_import)
            await self.db_session.commit()
            await self.db_session.refresh(new_import)
            return new_import
        except Exception as e:
            await self.db_session.rollback()
            raise e
