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


@pytest.mark.asyncio
async def test_update_product_must_be_success(
    product_repository: RepositoryInterface[ProductCreate, ProductUpdate, Product],
    create_product_instance: ProductCreate,
) -> None:
    new_product = await product_repository.save(create_product_instance)

    update_data = ProductUpdate(
        ncm="84159000",
        final_description="Ventilador industrial para sistemas de refrigeração"
    )

    updated_product = await product_repository.update(
        new_product.id, update_data
    )

    assert updated_product is not None
    assert updated_product.id == new_product.id
    assert updated_product.ncm == "84159000"
    assert updated_product.final_description == "Ventilador industrial para sistemas de refrigeração"
    assert updated_product.ncm != create_product_instance.ncm
    assert updated_product.final_description != create_product_instance.final_description


@pytest.mark.asyncio
async def test_list_all_product_must_be_success(
    product_repository: RepositoryInterface[
        ProductCreate, ProductUpdate, Product
    ],
    create_product_instance: ProductCreate,
) -> None:

    product_1 = await product_repository.save(create_product_instance)
    
    product_2 = await product_repository.save(
        ProductCreate(
            ncm="84159000",
            final_description="Ventilador industrial para sistemas de refrigeração"
        )
    )
    
    product_3 = await product_repository.save(
        ProductCreate(
            ncm="87032100",
            final_description="Parafuso para placas de circuito impresso"
        )
    )
    products_list = await product_repository.list_all()

    assert isinstance(products_list, list)
    assert len(products_list) >= 3  
    
 
    product_ids = [p.id for p in products_list]
    assert product_1.id in product_ids
    assert product_2.id in product_ids
    assert product_3.id in product_ids
    
    for product in products_list:
        assert isinstance(product, Product)