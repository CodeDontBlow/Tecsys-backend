from pydantic import ValidationError
import pytest
from app.model.imports import Imports
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.imports import ImportCreate, ImportUpdate
from app.repositories.imports_repository import ImportsRepository


@pytest.fixture
def import_repository(
    repository_factory,
) -> RepositoryInterface[ImportCreate, ImportUpdate, Imports]:
    """Fixture to provide an instace of ImportsRepository."""
    return repository_factory(Imports, ImportsRepository)


@pytest.fixture
def create_import_instance() -> ImportCreate:
    """Fixture to provide a valid instance of ImportCreate schema."""
    return ImportCreate(
        product_part_number="98765-ABC",
        order_id=1,
        manufacturer_id=1,
        supplier_product_id=1,
    )


@pytest.fixture
def update_import_instance() -> ImportUpdate:
    """Fixture to provide a valid instance of ImportUpdate schema."""
    return ImportUpdate(product_part_number="54321-DEF")


def test_invalid_create_import_instance():
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
