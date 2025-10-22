from pydantic import ValidationError
import pytest

from app.model.product import Product
from app.repositories.product_repository import ProductRepository
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.product import ProductCreate, ProductUpdate


@pytest.fixture
def product_repository(
    repository_factory,
) -> RepositoryInterface[ProductCreate, ProductUpdate, Product]:
    return repository_factory(Product, ProductRepository)


@pytest.fixture
def create_product_instance() -> ProductCreate:
    return ProductCreate(
        ncm="87032100",
        final_description="Parafuso para placas de circuito impresso",
    )


def test_invalid_product_create_instance_ncm_lenght():
    with pytest.raises(ValidationError):
        ProductCreate(
            ncm="123",  # too short, min_length=6
            final_description=12345,
        )


@pytest.mark.asyncio
async def test_create_product_must_be_success(
    product_repository: RepositoryInterface[ProductCreate, ProductUpdate, Product],
    create_product_instance: ProductCreate,
) -> None:
    new_product = await product_repository.save(create_product_instance)

    assert new_product is not None
    assert new_product.id is not None
    assert isinstance(new_product, Product)
    assert new_product.ncm == create_product_instance.ncm
    assert new_product.final_description == create_product_instance.final_description
