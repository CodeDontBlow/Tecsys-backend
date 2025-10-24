from typing import Tuple
from pydantic import ValidationError
import pytest
import pytest_asyncio
import datetime
from sympy import Product
from app.model.manufacturer import Manufacturer
from app.model.imports import Imports
from app.model.order import Order
from app.model.supplier import Supplier
from app.model.supplier_product import SupplierProduct
from app.repositories.manufacturer_repository import ManufacturerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.repository_interface import RepositoryInterface
from app.repositories.supplier_product_repository import SupplierProductRepository
from app.schemas.imports import ImportCreate, ImportUpdate
from app.schemas.manufacturer import ManufacturerCreate
from app.schemas.order import OrderCreate
from app.repositories.imports_repository import ImportsRepository
from app.schemas.supplier_product import SupplierProductCreate


@pytest_asyncio.fixture
async def create_order_product_manufacturer(
    repository_factory,
    create_supplier_and_product: Tuple[Supplier, Product],
    # order_repository
) -> Tuple[Order, Manufacturer, SupplierProduct]:
    order_repo = repository_factory(Order, OrderRepository)
    manufacturer_repo = repository_factory(Manufacturer, ManufacturerRepository)
    supplier_product_repo = repository_factory(
        SupplierProduct, SupplierProductRepository
    )

    order = await order_repo.save(
        OrderCreate(
            order_date=datetime.datetime.fromisoformat("2023-10-05T14:48:00.000Z")
        )
    )

    manufacturer = await manufacturer_repo.save(
        ManufacturerCreate(
            name="Manufacturer ABC",
            origin_country="Brazil",
            address="1234 Industrial Rd, City, Country",
        )
    )

    supplier, product = create_supplier_and_product

    supplier_product = await supplier_product_repo.save(
        SupplierProductCreate(
            supplier_id=supplier.id,
            product_id=product.id,
            erp_description="Test ERP Description",
        )
    )

    return order, manufacturer, supplier_product


@pytest.fixture
def import_repository(
    repository_factory,
) -> RepositoryInterface[ImportCreate, ImportUpdate, Imports]:
    """Fixture to provide an instace of ImportsRepository."""
    return repository_factory(Imports, ImportsRepository)


@pytest.fixture
def create_import_instance(
    create_order_product_manufacturer: Tuple[Order, Manufacturer, SupplierProduct],
) -> ImportCreate:
    """Fixture to provide a valid instance of ImportCreate schema."""
    order, manufacturer, supplier_product = create_order_product_manufacturer

    return ImportCreate(
        product_part_number="98765-ABC",
        order_id=order.id,
        manufacturer_id=manufacturer.id,
        supplier_product_id=supplier_product.id,
    )

def test_invalid_create_import_instance_must_raises_exc():
    """Test that creating an ImportCreate instance with invalid data raises a ValidationError."""
    with pytest.raises(ValidationError):
        ImportCreate(
            product_part_number="98765-ABC",
            order_id="invalid_txt",
            manufacturer_id=1,
            supplier_product_id=1,
        )


@pytest.mark.asyncio
async def test_create_import_must_be_success(
    import_repository: RepositoryInterface[ImportCreate, ImportUpdate, Imports],
    create_import_instance: ImportCreate,
) -> None:
    """Test that creating an import is successful."""

    new_import = await import_repository.save(create_import_instance)

    assert new_import is not None
    assert new_import.id is not None
    assert isinstance(new_import, Imports)
    assert new_import.product_part_number == create_import_instance.product_part_number
    assert new_import.order_id == create_import_instance.order_id
    assert new_import.manufacturer_id == create_import_instance.manufacturer_id
    assert new_import.supplier_product_id == create_import_instance.supplier_product_id
