from typing import Annotated
from app.schemas.order import OrderResponse
from app.schemas.supplier_product import SupplierProductResponse
from pydantic import BaseModel, Field
from app.schemas.manufacturer import ManufacturerBase, ManufacturerResponse


class ImportBase(BaseModel):
    """Base schema for import information"""
    product_part_number: Annotated[
        str,
        Field(
            title="Product Part Number",
            description="Part number of the product being imported",
            examples=["12345-XYZ"],
        ),
    ]

    order_id: Annotated[
        int,
        Field(
            title="Order ID",
            description="Unique identifier for the order associated with the import",
            examples=[1],
        ),
    ]
    manufacturer: Annotated[
        ManufacturerBase,
        Field(
            title="Manufacturer Information",
            description="Details of the manufacturer",
            examples=[{
                "name": "Manufacturer ABC",
                "origin_country": "Country XYZ",
                "address": "1234 Industrial Rd, City, Country",
            }],
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class ImportUpdate(BaseModel):
    product_part_number: Annotated[
        str | None,
        Field(
            title="Product Part Number",
            description="Part number of the product being imported",
            examples=["12345-XYZ"],
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
    }

class ImportResponse(BaseModel):
    id: int
    product_part_number: str
    manufacturer: ManufacturerResponse
    supplier_product: SupplierProductResponse
    order: OrderResponse