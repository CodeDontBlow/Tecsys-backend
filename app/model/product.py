from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.model.base import Base

class Product(Base):
    """Model for the products table."""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ncm: Mapped[str] = mapped_column(String(10), nullable=False)
    final_description: Mapped[str] = mapped_column(String(300), nullable=False)

    # supplyer_products: Mapped[list["SupplyerProduct"]] = relationship("SupplyerProduct")
    # supplyer_products: Mapped[list["SupplyerProduct"]] = relationship("SupplyerProduct", back_populates="product")
