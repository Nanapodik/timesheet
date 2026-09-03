from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import (
    get_current_admin,
    get_timesheet_fact_service,
)
from app.models.user import User
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
    current_user: User = Depends(get_current_admin),
) -> TimesheetFactResponse:
    try:
        fact = service.create(
            employee_id=data.employee_id,
            work_date=data.work_date,
            actual_hours=data.actual_hours,
        )

    except TimesheetFactFutureDateError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except TimesheetPlanNotFoundForFactError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except TimesheetFactHoursMismatchError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except TimesheetFactAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return TimesheetFactResponse.model_validate(fact)


@router.get(
    "",
    response_model=list[TimesheetFactResponse],
)
def get_timesheet_facts(
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
    current_user: User = Depends(get_current_admin),
) -> list[TimesheetFactResponse]:
    facts = service.get_all()

    return [
        TimesheetFactResponse.model_validate(fact)
        for fact in facts
    ]


@router.get(
    "/{timesheet_fact_id}",
    response_model=TimesheetFactResponse,
)
def get_timesheet_fact(
    timesheet_fact_id: int,
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
    current_user: User = Depends(get_current_admin),
) -> TimesheetFactResponse:
    try:
        fact = service.get_by_id(timesheet_fact_id)

    except TimesheetFactNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return TimesheetFactResponse.model_validate(fact)


@router.get(
    "/employee/{employee_id}",
    response_model=list[TimesheetFactResponse],
)
def get_timesheet_facts_by_employee(
    employee_id: int,
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
    current_user: User = Depends(get_current_admin),
) -> list[TimesheetFactResponse]:
    facts = service.get_by_employee_id(employee_id)

    return [
        TimesheetFactResponse.model_validate(fact)
        for fact in facts
    ]


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
    current_user: User = Depends(get_current_admin),
) -> TimesheetFactResponse:
    try:
        fact = service.update(
            timesheet_fact_id=timesheet_fact_id,
            actual_hours=data.actual_hours,
        )

    except TimesheetFactNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except TimesheetFactFutureDateError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except TimesheetPlanNotFoundForFactError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except TimesheetFactHoursMismatchError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return TimesheetFactResponse.model_validate(fact)


@router.delete(
    "/{timesheet_fact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_timesheet_fact(
    timesheet_fact_id: int,
    service: TimesheetFactService = Depends(
        get_timesheet_fact_service
    ),
    current_user: User = Depends(get_current_admin),
) -> None:
    try:
        service.delete(timesheet_fact_id)

    except TimesheetFactNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error