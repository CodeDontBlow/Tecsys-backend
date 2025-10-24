from typing import Annotated
from app.schemas.supplier import SupplierResponse
from pydantic import BaseModel, Field

from app.schemas.product import ProductResponse


class SupplierProductBase(BaseModel):
    """Base schema for supplier-product relationship"""

    supplier_id: Annotated[
        int,
        Field(
            title="Supplier ID",
            description="Unique identifier for the supplier",
            examples=[1],
        ),
    ]
    product_id: Annotated[
        int,
        Field(
            title="Product id",
            description="Primary key id of the product",
            examples=[1],
        ),
    ]
    erp_description: Annotated[
        str,
        Field(
            title="erp_descriptions",
            description="A relationship descriptions between Supplier and Product",
            examples=[1],
        )
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


class SupplierProductCreate(SupplierProductBase):
    model_config = SupplierProductBase.model_config


class SupplierProductUpdate(BaseModel):
    erp_description: Annotated[
        str | None,
        Field(
            title="erp_descriptions",
            description="A relationship descriptions between Supplier and Product",
            examples=[1],
        )
    ]

    part_number: Annotated[
        str | None,
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


class SupplierProductResponse(BaseModel):
    id: int
    erp_description: str
    supplier: SupplierResponse
    product: ProductResponse
