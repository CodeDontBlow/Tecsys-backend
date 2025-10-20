from typing import Tuple
import pytest
import pytest_asyncio

# Import the models
from app.model.supplier import Supplier
from app.model.product import Product
from app.model.supplier_product import SupplierProduct

# Import the repositories
from app.repositories.repository_interface import RepositoryInterface
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_product_repository import SupplierProductRepository

# Import the schemas
from app.schemas.product import ProductCreate
from app.schemas.supplier import SupplierCreate
from app.schemas.supplier_product import SupplierProductCreate


# @pytest_asyncio.fixture
# async def create_supplier_and_product(repository_factory) -> Tuple[Supplier, Product]:
#     """Create a supplier and a product for testing purposes."""
#     supplier_repo = repository_factory(Supplier, SupplierRepository)
#     product_repo = repository_factory(Product, ProductRepository)

#     supplier = await supplier_repo.save(
#         SupplierCreate(name="Supplier Test", part_number="PN12345")
#     )

#     product = await product_repo.save(
#         ProductCreate(ncm="PN12345", final_description="Supplier Test")
#     )

#     return supplier, product


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
