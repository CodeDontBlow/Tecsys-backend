from pydantic import BaseModel, Field
from typing import Annotated


class ManufacturerBase(BaseModel):
    """Base schema for manufacturer information"""
    name: Annotated[
        str,
        Field(
            title="Manufacturer Name",
            description="Name of the manufacturer",
            examples=["Manufacturer ABC"],
        ),
    ]

    origin_country: Annotated[
        str,
        Field(
            title="Manufacturer Name",
            description="Name of the manufacturer",
            examples=["Manufacturer ABC"],
        ),
    ]

    address: Annotated[
        str,
        Field(
            title="Manufacturer Address",
            description="Address of the manufacturer",
            examples=["1234 Industrial Rd, City, Country"],
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class ManufacturerUpdate(BaseModel):
    name: Annotated[
        str | None,
        Field(
            title="Manufacturer Name",
            description="Name of the manufacturer",
            examples=["Manufacturer ABC"],
        ),
    ]

    origin_country: Annotated[
        str | None,
        Field(
            title="Manufacturer Name",
            description="Name of the manufacturer",
            examples=["Manufacturer ABC"],
        ),
    ]

    address: Annotated[
        str | None,
        Field(
            title="Manufacturer Address",
            description="Address of the manufacturer",
            examples=["1234 Industrial Rd, City, Country"],
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
