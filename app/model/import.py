from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String

from app.model.order import Order


class Import(DeclarativeBase):
    """Model for the imports table."""
    __tablename__ = "imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_part_number: Mapped[str] = mapped_column(String(20),nullable=False)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(Integer, ForeignKey("manufacturers.id"), nullable=False)
    supplyer_product_id: Mapped[int] = mapped_column(Integer, ForeignKey("supplyer_products.id"), nullable=False)

    order: Mapped[Order] = relationship("Pedido", back_populates="imports")
    manufacturer: Mapped["Manufacturer"] = relationship("Manufacturer", back_populates="imports")
    supplyer_product: Mapped["SupplyerProduct"] = relationship("SupplyerProduct", back_populates="imports")