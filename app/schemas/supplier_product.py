from typing import Annotated
from pydantic import BaseModel, Field

from app.schemas.product import ProductBase


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
            title="Product id", description="Primary key id of the product", examples=[1]
        ),
    ]
    erp_description: Annotated[
        str,
        Field(
            title="Product ERP description",
            description="ERP description of the product extracted from pdf",
            examples=["Some product description"],
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class SupplierProductCreate(SupplierProductBase):
    """Schema for creating a supplier-product relationship"""
    pass


class SupplierProductUpdate(BaseModel):
    erp_description: str
