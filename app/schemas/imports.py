from typing import Annotated
from app.schemas.order import OrderResponse
from app.schemas.supplier_product import SupplierProductResponse
from pydantic import BaseModel, Field
from app.schemas.manufacturer import ManufacturerResponse


class ImportBase(BaseModel):
    """Base schema for import information"""
    product_part_number: Annotated[
        str,
        Field(
            title="Product Part Number",
            description="Part number of the product being imported",
            examples=["12345-XYZ"],
            max_length=30,
            min_length=1
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class ImportCreate(ImportBase):
    order_id: Annotated[
        int,
        Field(
            title="Order ID",
            description="ID of the order associated with the import",
            examples=[1],
        ),
    ]

    manufacturer_id: Annotated[
        int,
        Field(
            title="Manufacter ID",
            description="ID of the Manufacter associated with the product and import",
            examples=[1],
        ),
    ]

    supplier_product_id: Annotated[
        int,
        Field(
            title="Order ID",
            description="ID of the supplier and product relationship associated with the import",
            examples=[1],
        ),
    ]


class ImportUpdate(ImportBase):
    product_part_number: Annotated[
        str | None,
        Field(
            title="Product Part Number",
            description="Part number of the product being imported",
            examples=["12345-XYZ"],
        ),
    ]

    model_config = BaseModel.model_config


class ImportResponse(BaseModel):
    id: int
    product_part_number: str
    manufacturer: ManufacturerResponse
    supplier_product: SupplierProductResponse
    order: OrderResponse
