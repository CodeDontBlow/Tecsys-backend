from pydantic import BaseModel, Field
from typing import Annotated


class ProductBase(BaseModel):
    '''Base schema for product information'''
    id: Annotated[int, Field(title="Product id", description="ID product primary key", examples=1)]
    ncm: Annotated[str, Field(title="Product NCM code", description="NCM code of the product", examples="87032100")]
    # descricao_ncm: Annotated[str, Field(title="Product Description by NCM", description="Description of the product according to its NCM code", examples="")]
    final_description: Annotated[str, Field(title="Product Final descriptrion", description="Final description of the product by Embedding Model", examples="")]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "orm_mode": True,
    }

class ProductUpdate(BaseModel):
    ncm:str
    final_description:str



