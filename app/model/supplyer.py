from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer


class Supplyer(DeclarativeBase):
    """Model for suppliers table."""
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    part_number: Mapped[str] = mapped_column(String(20), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    supplyer_products: Mapped[list["SupplyerProduct"]] = relationship("SupplyerProduct", back_populates="suppliers")
