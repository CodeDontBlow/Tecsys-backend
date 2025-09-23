from typing import Annotated
from pydantic import BaseModel, Field

from app.schemas.manufacturer import ManufacturerBase


class ImportBase(BaseModel):
    """ Base schema for import information """
    id: Annotated[int, Field(title="ID", description="Unique identifier for the import", examples=1)]
    product_part_number: Annotated[str, Field(title="Product Part Number", description="Part number of the product being imported", examples="12345-XYZ")]
    order_id: Annotated[int, Field(title="Order ID", description="Unique identifier for the order associated with the import", examples=1)]
    manufacturer: Annotated[ManufacturerBase, Field(title="Manufacturer Information", description="Details of the manufacturer", examples={"name": "Manufacturer ABC", "origin_country": "Country XYZ", "address": "1234 Industrial Rd, City, Country"})]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "orm_mode": True,
    }