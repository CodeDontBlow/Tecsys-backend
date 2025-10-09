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
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class SupplierUpdate(BaseModel):
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

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
