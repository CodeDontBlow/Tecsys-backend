from datetime import date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Date
from app.model.base import Base
from sqlalchemy.orm import relationship



class Order(Base):
    """Model for the orders table."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    
    imports = relationship("Imports", back_populates="order")