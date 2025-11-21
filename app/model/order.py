from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, DateTime
from app.model.base import Base
from sqlalchemy.orm import relationship


class Order(Base):
    """Model for the orders table."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    imports = relationship("Imports", back_populates="order")
