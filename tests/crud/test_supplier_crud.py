from pydantic import ValidationError
import pytest

from app.model.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.repository_interface import RepositoryInterface


@pytest.fixture
def supplier_repository(
    repository_factory,
) -> RepositoryInterface[SupplierCreate, SupplierUpdate, Supplier]:
    return repository_factory(Supplier, SupplierRepository)


@pytest.fixture
def create_supplier_instance() -> SupplierCreate:
    return SupplierCreate(
        part_number="PN12345",
        name="Supplier A",
    )


def test_invalid_pn_lenght_supplier_instace_must_raise_error() -> None:
    with pytest.raises(ValidationError):
        SupplierCreate(
            part_number="P" * 31,  # Exceeds max length of 30
            name="Supplier A",
        )


@pytest.mark.asyncio
async def test_save_supplier_must_be_success(
    supplier_repository: RepositoryInterface[SupplierCreate, SupplierUpdate, Supplier],
    create_supplier_instance: SupplierCreate,
) -> None:
    new_supplier = await supplier_repository.save(create_supplier_instance)

    assert new_supplier is not None
    assert new_supplier.id is not None
    assert isinstance(new_supplier, Supplier)
    assert new_supplier.part_number == create_supplier_instance.part_number
    assert new_supplier.name == create_supplier_instance.name
