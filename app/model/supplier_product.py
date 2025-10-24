from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey

from app.model.base import Base


class SupplierProduct(Base):
    """Model for the relationship between suppliers and products."""

    __tablename__ = "supplier_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # part_number: Mapped[str] = mapped_column(String(30), nullable=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )
    erp_description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    imports = relationship("Imports", back_populates="supplier_product")
    product = relationship("Product", back_populates="supplier_product") 
    supplier = relationship("Supplier", back_populates="supplier_product")

    # supplyer: Mapped["Supplyer"] = relationship("Supplyer")
    # product: Mapped["Product"] = relationship("Product")

    # imports: Mapped[list["Import"]] = relationship("Import")
    # supplyer: Mapped["Supplyer"] = relationship("Supplyer", back_populates="supplyer_products")
    # product: Mapped["Product"] = relationship("Product", back_populates="supplyer_products")
    # imports: Mapped[list["Import"]] = relationship("Import", back_populates="supplyer_product")
