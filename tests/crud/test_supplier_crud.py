from app.schemas.product import ProductCreate, ProductUpdate
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
    assert new_supplier.name == create_supplier_instance.name


@pytest.mark.asyncio
async def test_update_supplier_must_be_success(
    supplier_repository: RepositoryInterface[SupplierCreate, SupplierUpdate, Supplier],
    create_supplier_instance: SupplierCreate,
) -> None:  
    new_supplier = await supplier_repository.save(create_supplier_instance)

    update_data = SupplierUpdate(
        name="Updated Supplier B"
    )

    updated_supplier = await supplier_repository.update(
        new_supplier.id, update_data
    )

    assert updated_supplier is not None
    assert updated_supplier.id == new_supplier.id
    assert updated_supplier.name == "Updated Supplier B"
    assert updated_supplier.name != create_supplier_instance.name

@pytest.mark.asyncio
async def test_list_all_supplier_must_be_success(
    supplier_repository: RepositoryInterface[
        SupplierCreate, SupplierUpdate, Supplier
    ],
    create_supplier_instance: SupplierCreate,
) -> None:

    supplier_1 = await supplier_repository.save(create_supplier_instance)
    
    supplier_2 = await supplier_repository.save(
        SupplierCreate(
            name="Supplier B"
        )
    )
    
    supplier_3 = await supplier_repository.save(
        SupplierCreate(
            name="Supplier C"
        )
    )
    
    suppliers_list = await supplier_repository.list_all()

    assert isinstance(suppliers_list, list)
    assert len(suppliers_list) >= 3  
    
 
    supplier_ids = [p.id for p in suppliers_list]
    assert supplier_1.id in supplier_ids
    assert supplier_2.id in supplier_ids
    assert supplier_3.id in supplier_ids
    
    for supplier in suppliers_list:
        assert isinstance(supplier, Supplier)