from datetime import date

from pydantic import BaseModel


class TimesheetReportDay(BaseModel):
    work_date: date
    planned_hours: float
    actual_hours: float | None


class TimesheetReportResponse(BaseModel):
    employee_id: int
    year: int
    month: int

    planned_total: float
    actual_total: float
    difference: float

    days: list[TimesheetReportDay]