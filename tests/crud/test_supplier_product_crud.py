import pytest

# Import the models

from app.model.supplier_product import SupplierProduct

# Import the repositories
from app.repositories.repository_interface import RepositoryInterface
from app.repositories.supplier_product_repository import SupplierProductRepository

# Import the schemas
from app.schemas.supplier_product import SupplierProductCreate

@pytest.fixture
def supplier_product_repository(repository_factory) -> RepositoryInterface:
    """Fixture to provide an instace of SupplierProductRepository."""
    return repository_factory(SupplierProduct, SupplierProductRepository)


@pytest.fixture
def create_supplier_product_instance(
    create_supplier_and_product,
) -> SupplierProductCreate:
    """Fixture to create a SupplierProduct instance."""
    supplier, product = create_supplier_and_product

    return SupplierProductCreate(
        supplier_id=supplier.id,
        product_id=product.id,
        erp_description="Test ERP Description",
        part_number="PN12345",
    )


@pytest.mark.asyncio
async def test_create_supplier_product(
    supplier_product_repository,
    create_supplier_product_instance,
    create_supplier_and_product,
) -> None:
    """Test creating a SupplierProduct."""    
    supplier_product = await supplier_product_repository.save(
        create_supplier_product_instance
    )

    assert supplier_product.id is not None
    assert supplier_product.supplier_id == create_supplier_product_instance.supplier_id
    assert supplier_product.product_id == create_supplier_product_instance.product_id
    assert supplier_product.part_number == create_supplier_product_instance.part_number
