from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_timesheet_fact_service
from app.schemas.timesheet_fact import (
    TimesheetFactCreate,
    TimesheetFactResponse,
    TimesheetFactUpdate,
)
from app.services.timesheet_fact import (
    TimesheetFactAlreadyExistsError,
    TimesheetFactFutureDateError,
    TimesheetFactHoursMismatchError,
    TimesheetFactNotFoundError,
    TimesheetFactService,
    TimesheetPlanNotFoundForFactError,
)


router = APIRouter(
    prefix="/timesheet-facts",
    tags=["Timesheet Facts"],
)


@router.post(
    "",
    response_model=TimesheetFactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_timesheet_fact(
    data: TimesheetFactCreate,
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
):
    try:
        return service.create(
            employee_id=data.employee_id,
            work_date=data.work_date,
            actual_hours=data.actual_hours,
        )

    except TimesheetFactAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except TimesheetFactFutureDateError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except TimesheetFactHoursMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except TimesheetPlanNotFoundForFactError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[TimesheetFactResponse],
)
def get_timesheet_facts(
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
):
    return service.get_all()


@router.get(
    "/employee/{employee_id}",
    response_model=list[TimesheetFactResponse],
)
def get_employee_timesheet_facts(
    employee_id: int,
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
):
    return service.get_by_employee_id(employee_id)


@router.get(
    "/{timesheet_fact_id}",
    response_model=TimesheetFactResponse,
)
def get_timesheet_fact(
    timesheet_fact_id: int,
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
):
    try:
        return service.get_by_id(timesheet_fact_id)

    except TimesheetFactNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/{timesheet_fact_id}",
    response_model=TimesheetFactResponse,
)
def update_timesheet_fact(
    timesheet_fact_id: int,
    data: TimesheetFactUpdate,
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
):
    try:
        return service.update(
            timesheet_fact_id=timesheet_fact_id,
            actual_hours=data.actual_hours,
        )

    except TimesheetFactNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except TimesheetFactFutureDateError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except TimesheetFactHoursMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except TimesheetPlanNotFoundForFactError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{timesheet_fact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_timesheet_fact(
    timesheet_fact_id: int,
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
):
    try:
        service.delete(timesheet_fact_id)

    except TimesheetFactNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc