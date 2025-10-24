from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from app.model.base import Base


class Supplier(Base):
    """Model for suppliers table."""
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    supplier_product = relationship("SupplierProduct", back_populates="supplier")

    # supplyer_products: Mapped[list["SupplyerProduct"]] = relationship("SupplyerProduct")
    # supplyer_products: Mapped[list["SupplyerProduct"]] = relationship("SupplyerProduct", back_populates="suppliers")
