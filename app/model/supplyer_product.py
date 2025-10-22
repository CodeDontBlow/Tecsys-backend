from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey

from app.model.base import Base


class SupplyerProduct(Base):
    """Model for the relationship between suppliers and products."""
    __tablename__ = "supplyer_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplyer_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=False)
    product_ncm: Mapped[str] = mapped_column(String(10), ForeignKey("products.ncm"), nullable=False)
    erp_description: Mapped[str] = mapped_column(String(255), nullable=True)

    supplyer: Mapped["Supplyer"] = relationship("Supplyer", back_populates="supplyer_products")
    product: Mapped["Product"] = relationship("Product", back_populates="supplyer_products")
    imports: Mapped[list["Import"]] = relationship("Import", back_populates="supplyer_product")
