from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class TimesheetFact(Base):
    __tablename__ = "timesheet_facts"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "work_date",
            name="uq_timesheet_fact_employee_date",
        ),
    )

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