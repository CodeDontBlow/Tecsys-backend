from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")
TModel = TypeVar("TModel")


class RepositoryInterface(ABC, Generic[TCreate, TUpdate, TModel]):
    @abstractmethod
    async def save(self, obj_data: TCreate) -> TModel:
        pass

    @abstractmethod
    async def list_all(self) -> List[TModel]:
        pass

    @abstractmethod
    async def get_by_id(self, obj_id: int) -> Optional[TModel]:
        pass

    @abstractmethod
    async def update(self, obj_data: TUpdate) -> TModel:
        pass

    @abstractmethod
    async def delete(self, obj_id: int) -> None:
        pass
