from typing import Annotated
from pydantic import BaseModel, Field
from datetime import datetime


class OrderBase(BaseModel):
    '''Base schema for order information'''
    id: Annotated[int, Field(title="ID", description="Unique identifier for the order", examples=1)]
    order_date: Annotated[datetime, Field(title="Order Date", description="Date when the order was placed", examples="2023-10-05T14:48:00.000Z")]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "orm_mode": True,
    }