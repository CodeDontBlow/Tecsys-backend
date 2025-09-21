from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey


class SupplyerProduct(DeclarativeBase):
    """Model for the relationship between suppliers and products."""
    __tablename__ = "supplyer_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplyer_id: Mapped[int] = mapped_column(Integer, ForeignKey("supplyers.id"), nullable=False)
    product_ncm: Mapped[str] = mapped_column(String(10), ForeignKey("products.ncm"), nullable=False)

    supplyer: Mapped["Supplyer"] = relationship("Supplyer", back_populates="supplyer_products")
    product: Mapped["Product"] = relationship("Product", back_populates="supplyer_products")
    imports: Mapped[list["Import"]] = relationship("Import", back_populates="supplyer_product")
