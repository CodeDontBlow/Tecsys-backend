from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Product(DeclarativeBase):
    __tablename__ = "products"

    ncm: Mapped[str] = mapped_column(String(10), primary_key=True, unique=True, nullable=False)
    final_description: Mapped[str] = mapped_column(String(300), nullable=False)
