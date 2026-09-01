from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class TimesheetFact(Base):
    __tablename__ = "timesheet_facts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
    )

    work_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    actual_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )