from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String


class Supplyer(DeclarativeBase):
    __tablename__ = "supplyers"

    part_number: Mapped[str] = mapped_column(String(20), primary_key=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
