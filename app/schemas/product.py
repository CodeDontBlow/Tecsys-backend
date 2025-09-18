from pydantic import BaseModel, Field
from typing import Annotated


class ProductBase(BaseModel):
    '''Base schema for product information'''
    ncm: Annotated[str, Field(title="Product NCM code", description="NCM code of the product", examples="87032100")]
    descricao_ncm: Annotated[str, Field(title="Product Description by NCM", description="Description of the product according to its NCM code", examples="")]
    descricao_final: Annotated[str, Field(title="Product Final descriptrion", description="Final description of the product by LLM Model", examples="")]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
    }


class ProductCreate(ProductBase):
    pass
