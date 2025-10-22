from pydantic import BaseModel, Field
from typing import Annotated

class ProductBase(BaseModel):
    """Base schema for product information"""

    id: Annotated[
        int, Field(title="Product id", description="ID product primary key", examples=[1])
    ]

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


class ProductUpdate(BaseModel):
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


class ProductResponse(BaseModel):
    id: int
    description_di: str = Field(alias="final_description")     