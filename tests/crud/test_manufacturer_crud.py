import pytest
from pydantic import ValidationError

from app.model.manufacturer import Manufacturer
from app.repositories.manufacturer_repository import ManufacturerRepository
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.manufacturer import ManufacturerCreate, ManufacturerUpdate


@pytest.fixture
def manufacturer_repository(
    repository_factory,
) -> RepositoryInterface[ManufacturerCreate, ManufacturerUpdate, Manufacturer]:
    return repository_factory(Manufacturer, ManufacturerRepository)


@pytest.fixture
def manufacturer_create_instace() -> ManufacturerCreate:
    return ManufacturerCreate(
        name="Manufacturer ABC",
        # origin_country="Brazil",
        # address="1234 Industrial Rd, City, Country",
    )


def test_invalid_type_for_name_must_raise_exc() -> None:
    with pytest.raises(ValidationError):
        return ManufacturerCreate(
            name=123,  # wrong int type
            # origin_country="Brazil",
            # address="1234 Industrial Rd, City, Country",
        )


@pytest.mark.asyncio
async def test_save_manufacturer_must_be_success(
    manufacturer_repository: RepositoryInterface[
        ManufacturerCreate, ManufacturerUpdate, Manufacturer
    ],
    manufacturer_create_instace: Manufacturer,
) -> None:
    new_manufacturer = await manufacturer_repository.save(manufacturer_create_instace)

    assert new_manufacturer is not None
    assert new_manufacturer.id is not None
    assert isinstance(new_manufacturer, Manufacturer)
    assert new_manufacturer.name == manufacturer_create_instace.name
    # assert new_manufacturer.origin_country == manufacturer_create_instace.origin_country
    # assert new_manufacturer.address == manufacturer_create_instace.address
