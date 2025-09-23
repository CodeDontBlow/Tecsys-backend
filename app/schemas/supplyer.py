from typing import Annotated
from pydantic import BaseModel, Field


class BaseSupplyer(BaseModel):
    '''Base schema for supplyer information'''
    id: Annotated[int, Field(title="ID", description="Unique identifier for the supplyer", examples=1)]
    name: Annotated[str, Field(title="Supplyer Name", description="Name of the supplyer", examples="Supplyer XYZ")]
    part_number: Annotated[str, Field(title="Part Number", description="Part number of the supplyer", examples="12345-XYZ")]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "orm_mode": True,
    }


class SupplyerCreate(BaseSupplyer):
    pass
