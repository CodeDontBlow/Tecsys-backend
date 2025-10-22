from typing import Annotated
from pydantic import BaseModel, Field
from datetime import datetime


class OrderBase(BaseModel):
    """Base schema for order information"""
    order_date: Annotated[
        datetime,
        Field(
            title="Order Date",
            description="Date when the order was placed",
            examples=["2023-10-05T14:48:00.000Z"],
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    order_date: Annotated[
        datetime | None,
        Field(
            title="Order Date",
            description="Date when the order was placed",
            examples=["2023-10-05T14:48:00.000Z"],
        ),
    ]

    model_config = OrderBase.model_config


class OrderResponse(BaseModel):
    id: int
    order_date: datetime
