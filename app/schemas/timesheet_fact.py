from datetime import date

from pydantic import BaseModel, Field


class TimesheetFactCreate(BaseModel):
    employee_id: int
    work_date: date
    actual_hours: float = Field(ge=0, le=24)


class TimesheetFactUpdate(BaseModel):
    actual_hours: float = Field(ge=0, le=24)


class TimesheetFactResponse(BaseModel):
    id: int
    employee_id: int
    work_date: date
    actual_hours: float

    model_config = {
        "from_attributes": True
    }