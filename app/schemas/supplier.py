from typing import Annotated
from pydantic import BaseModel, Field


class BaseSupplier(BaseModel):
    """Base schema for supplier information"""
    name: Annotated[
        str,
        Field(
            title="Supplier Name",
            description="Name of the supplier",
            examples=["Supplier XYZ"],
        ),
    ]

    part_number: Annotated[
        str,
        Field(
            title="Part Number",
            description="Part number of the supplier",
            examples=["12345-XYZ"],
            max_length=30,
            min_length=1,
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class SupplierCreate(BaseSupplier):
    model_config = BaseSupplier.model_config


class SupplierUpdate(BaseSupplier):
    name: Annotated[
        str | None,
        Field(
            title="Supplier Name",
            description="Name of the supplier",
            examples=["Supplier XYZ"],
        ),
    ]

    part_number: Annotated[
        str | None,
        Field(
            title="Part Number",
            description="Part number of the supplier",
            examples=["12345-XYZ"],
        ),
    ]

    model_config = BaseSupplier.model_config


class SupplierResponse(BaseModel):
    id: int
    name: str
    part_number: str
