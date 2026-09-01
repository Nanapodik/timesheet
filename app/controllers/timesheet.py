from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_timesheet_service
from app.schemas.timesheet import (
    TimesheetPlanCreate,
    TimesheetPlanResponse,
    TimesheetPlanUpdate,
)
from app.services.employee import EmployeeNotFoundError
from app.services.timesheet import (
    TimesheetPlanNotFoundError,
    TimesheetPlanService,
)


router = APIRouter(
    prefix="/timesheet-plans",
    tags=["Timesheet Plans"],
)


@router.post(
    "",
    response_model=TimesheetPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_timesheet_plan(
    data: TimesheetPlanCreate,
    service: TimesheetPlanService = Depends(get_timesheet_service),
) -> TimesheetPlanResponse:
    try:
        timesheet_plan = service.create(
            employee_id=data.employee_id,
            work_date=data.work_date,
            planned_hours=data.planned_hours,
        )
    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return TimesheetPlanResponse.model_validate(timesheet_plan)


@router.get(
    "",
    response_model=list[TimesheetPlanResponse],
)
def get_timesheet_plans(
    service: TimesheetPlanService = Depends(get_timesheet_service),
) -> list[TimesheetPlanResponse]:
    timesheet_plans = service.get_all()

    return [
        TimesheetPlanResponse.model_validate(timesheet_plan)
        for timesheet_plan in timesheet_plans
    ]


@router.get(
    "/{timesheet_plan_id}",
    response_model=TimesheetPlanResponse,
)
def get_timesheet_plan(
    timesheet_plan_id: int,
    service: TimesheetPlanService = Depends(get_timesheet_service),
) -> TimesheetPlanResponse:
    timesheet_plan = service.get_by_id(timesheet_plan_id)

    if timesheet_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timesheet plan with id={timesheet_plan_id} not found",
        )

    return TimesheetPlanResponse.model_validate(timesheet_plan)


@router.get(
    "/employee/{employee_id}",
    response_model=list[TimesheetPlanResponse],
)
def get_employee_timesheet_plans(
    employee_id: int,
    service: TimesheetPlanService = Depends(get_timesheet_service),
) -> list[TimesheetPlanResponse]:
    try:
        timesheet_plans = service.get_by_employee_id(employee_id)
    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return [
        TimesheetPlanResponse.model_validate(timesheet_plan)
        for timesheet_plan in timesheet_plans
    ]


@router.put(
    "/{timesheet_plan_id}",
    response_model=TimesheetPlanResponse,
)
def update_timesheet_plan(
    timesheet_plan_id: int,
    data: TimesheetPlanUpdate,
    service: TimesheetPlanService = Depends(get_timesheet_service),
) -> TimesheetPlanResponse:
    try:
        timesheet_plan = service.update(
            timesheet_plan_id=timesheet_plan_id,
            work_date=data.work_date,
            planned_hours=data.planned_hours,
        )
    except TimesheetPlanNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return TimesheetPlanResponse.model_validate(timesheet_plan)


@router.delete(
    "/{timesheet_plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_timesheet_plan(
    timesheet_plan_id: int,
    service: TimesheetPlanService = Depends(get_timesheet_service),
) -> Response:
    try:
        service.delete(timesheet_plan_id)
    except TimesheetPlanNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)