from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base


class Product(Base):
    """Model for the products table."""
    __tablename__ = "products"

    ncm: Mapped[str] = mapped_column(String(10), primary_key=True, unique=True, nullable=False)
    final_description: Mapped[str] = mapped_column(String(300), nullable=False)

    supplyer_products: Mapped[list["SupplyerProduct"]] = relationship("SupplyerProduct", back_populates="products")
