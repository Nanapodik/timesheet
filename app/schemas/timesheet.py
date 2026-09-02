from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class TimesheetPlanCreate(BaseModel):
    employee_id: int
    work_date: date
    planned_hours: float = Field(ge=0, le=24)


class TimesheetPlanUpdate(BaseModel):
    work_date: date
    planned_hours: float = Field(ge=0, le=24)


class TimesheetPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    work_date: date
    planned_hours: float
    is_fixed: bool