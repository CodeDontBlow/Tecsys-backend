from typing import Annotated
from app.schemas.supplier import SupplierResponse
from pydantic import BaseModel, Field

from app.schemas.product import ProductBase, ProductResponse


class SupplierProductBase(BaseModel):
    """Base schema for supplier-product relationship"""

    id: Annotated[
        int,
        Field(
            title="ID",
            description="Unique identifier for the supplier-product relationship",
            examples=[1],
        ),
    ]
    supplier_id: Annotated[
        int,
        Field(
            title="Supplier ID",
            description="Unique identifier for the supplier",
            examples=[1],
        ),
    ]
    product_id: Annotated[
        int,
        Field(
            title="Product id", description="Primary key id of the product", examples=[1]
        ),
    ]
    product_ncm: Annotated[
        str,
        Field(
            title="Product NCM code",
            description="NCM code of the product",
            examples=["87032100"],
        ),
    ]
    product: Annotated[
        ProductBase,
        Field(
            title="Product Final description",
            description="Final description of the product by LLM Model",
            examples=["Some product description"],
        ),
    ]

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "from_attributes": True,
    }


class SupplierProductUpdate(BaseModel):
    erp_description: str

class SupplierProductResponse(BaseModel):
    id: int
    erp_description: str
    supplier: SupplierResponse
    product: ProductResponse


    #   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # supplier_id: Mapped[int] = mapped_column(
    #     Integer, ForeignKey("suppliers.id"), nullable=False
    # )
    # product_id: Mapped[str] = mapped_column(
    #     Integer, ForeignKey("products.id"), nullable=False
    # )
    # erp_description: Mapped[str] = mapped_column(String(255), nullable=True)