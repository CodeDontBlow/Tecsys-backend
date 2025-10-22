import datetime
from pydantic import ValidationError
import pytest

from app.model.order import Order
from app.repositories.order_repository import OrderRepository
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.order import OrderCreate, OrderUpdate


@pytest.fixture
def order_repository(
    repository_factory,
) -> RepositoryInterface[OrderCreate, OrderUpdate, Order]:
    return repository_factory(Order, OrderRepository)


@pytest.fixture
def order_create_instance() -> OrderCreate:
    return OrderCreate(
        order_date=datetime.datetime.fromisoformat("2023-10-05T14:48:00.000Z")
    )


def test_invalid_type_for_order_date_must_raise_exc() -> None:
    with pytest.raises(ValidationError):
        OrderCreate(
            order_date="string"  # wrong type
        )


@pytest.mark.asyncio    
async def test_save_order_must_be_success(
    order_repository: RepositoryInterface[OrderCreate, OrderUpdate, Order],
    order_create_instance: OrderCreate
) -> None:
    new_order = await order_repository.save(order_create_instance)

    assert new_order is not None
    assert new_order.id is not None
    assert isinstance(new_order, Order)
    # assert new_order.order_date == order_create_instance.order_date
