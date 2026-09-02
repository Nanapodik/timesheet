from fastapi import APIRouter, Depends

from app.dependencies import get_timesheet_report_service
from app.schemas.timesheet_report import TimesheetReportResponse
from app.services.timesheet_report import TimesheetReportService


router = APIRouter(
    prefix="/timesheet-reports",
    tags=["Timesheet Reports"],
)


@router.get(
    "/employee/{employee_id}/month/{year}/{month}",
    response_model=TimesheetReportResponse,
)
def get_month_timesheet_report(
    employee_id: int,
    year: int,
    month: int,
    service: TimesheetReportService = Depends(
        get_timesheet_report_service
    ),
) -> TimesheetReportResponse:

    return service.get_month_report(
        employee_id=employee_id,
        year=year,
        month=month,
    )