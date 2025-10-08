from typing import Annotated
from pydantic import BaseModel, Field

from app.schemas.product import ProductBase


class SupplyerProductBase(BaseModel):
    '''Base schema for supplyer-product relationship'''
    id: Annotated[int, Field(title="ID", description="Unique identifier for the supplyer-product relationship", examples=1)]
    supplyer_id: Annotated[int, Field(title="Supplyer ID", description="Unique identifier for the supplyer", examples=1)]
    product_id: Annotated[int, Field(title="Product id", description="Primary key id of the product", examples=1)]
    product_ncm: Annotated[str, Field(title="Product NCM code", description="NCM code of the product", examples="87032100")]
    product: Annotated[ProductBase, Field(title="Product Final description", description="Final description of the product by LLM Model", examples="Some product description")]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "orm_mode": True,
    }

class SupplierProductUpdate(BaseModel): 
    erp_description:str