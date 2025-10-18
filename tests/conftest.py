import asyncio
from typing import AsyncGenerator, Type
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.model.base import Base
from app.model.imports import Imports
from app.model.manufacturer import Manufacturer
from app.model.product import Product
from app.model.supplier import Supplier
from app.model.order import Order
from app.model.supplier_product import SupplierProduct

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    url=TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)

session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    """Create the database and tables for testing."""
    async with test_engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Create an event loop for the tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_teardown_database():
    """Setup and teardown the test database."""
    await create_db_and_tables()
    yield


@pytest_asyncio.fixture
async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a new database session for a test."""
    async with session_maker() as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def repository_factory(get_test_session: AsyncSession):
    """Factory to create repository instances for testing."""

    def _factory(model_cls: Type[Base], repo_cls: Type):
        return repo_cls(db_session=get_test_session, model=model_cls)

    return _factory
