from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Manufacturer(DeclarativeBase):
    """Model for the Manufacturers table."""
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(150), nullable=False)
    origin_country: Mapped[str] = mapped_column(String(50), nullable=False)