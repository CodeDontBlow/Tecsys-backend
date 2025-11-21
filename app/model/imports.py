from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String
from app.model.base import Base
from sqlalchemy.orm import relationship


class Imports(Base):
    """Model for the imports table."""

    __tablename__ = "imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_part_number: Mapped[str] = mapped_column(String(30), nullable=False)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), nullable=False
    )
    manufacturer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("manufacturers.id"), nullable=False
    )
    supplier_product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("supplier_products.id"), nullable=False
    )

    order = relationship("Order", back_populates="imports")
    manufacturer = relationship("Manufacturer", back_populates="imports")
    supplier_product = relationship("SupplierProduct", back_populates="imports")

    # order: Mapped["Order"] = relationship("Order")
    # manufacturer: Mapped["Manufacturer"] = relationship("Manufacturer")
    # supplyer_product: Mapped["SupplyerProduct"] = relationship("SupplyerProduct")

    # order: Mapped["Order"] = relationship("Order", back_populates="imports")
    # manufacturer: Mapped["Manufacturer"] = relationship("Manufacturer", back_populates="imports")
    # supplyer_product: Mapped["SupplyerProduct"] = relationship("SupplyerProduct", back_populates="imports")
