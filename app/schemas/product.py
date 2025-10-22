from pydantic import BaseModel, Field
from typing import Annotated


class ProductBase(BaseModel):
    """Base schema for product information"""
    ncm: Annotated[
        str,
        Field(
            title="Product NCM code",
            description="NCM code of the product",
            examples=["87032100"],
        ),
    ]

    final_description: Annotated[
        str,
        Field(
            title="Product Final descriptrion",
            description="Final description of the product by Embedding Model",
            # examples=[""],
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    ncm: Annotated[
        str | None,
        Field(
            title="Product NCM code",
            description="NCM code of the product",
            examples=["87032100"],
        ),
    ]

    final_description: Annotated[
        str | None,
        Field(
            title="Product Final descriptrion",
            description="Final description of the product by Embedding Model",
            # examples="",
        ),
    ]

    model_config = ProductBase.model_config


class ProductResponse(BaseModel):
    id: int
    description_di: str = Field(alias="final_description")
