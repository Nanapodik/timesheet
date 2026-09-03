from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import (
    get_current_user,
    get_timesheet_service,
)

from app.models.user import User

from app.schemas.timesheet import (
    TimesheetPlanCreate,
    TimesheetPlanResponse,
    TimesheetPlanUpdate,
)

from app.services.employee import EmployeeNotFoundError

from app.services.timesheet import (
    TimesheetMonthAlreadyFixedError,
    TimesheetPlanAlreadyExistsError,
    TimesheetPlanFixedError,
    TimesheetPlanNotFoundError,
    TimesheetPlanService,
)


router = APIRouter(
    prefix="/timesheet-plans",
    tags=["Timesheet Plans"],
)


# ============================================================
# CREATE
# ============================================================

@router.post(
    "",
    response_model=TimesheetPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_timesheet_plan(
    data: TimesheetPlanCreate,
    service: TimesheetPlanService = Depends(
        get_timesheet_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
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

    except TimesheetPlanAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except TimesheetMonthAlreadyFixedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return TimesheetPlanResponse.model_validate(
        timesheet_plan
    )


# ============================================================
# GET ALL
# ============================================================

@router.get(
    "",
    response_model=list[TimesheetPlanResponse],
)
def get_timesheet_plans(
    service: TimesheetPlanService = Depends(
        get_timesheet_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
) -> list[TimesheetPlanResponse]:

    timesheet_plans = service.get_all()

    return [
        TimesheetPlanResponse.model_validate(
            timesheet_plan
        )
        for timesheet_plan in timesheet_plans
    ]


# ============================================================
# GET BY ID
# ============================================================

@router.get(
    "/{timesheet_plan_id}",
    response_model=TimesheetPlanResponse,
)
def get_timesheet_plan(
    timesheet_plan_id: int,
    service: TimesheetPlanService = Depends(
        get_timesheet_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
) -> TimesheetPlanResponse:

    try:
        timesheet_plan = service.get_by_id(
            timesheet_plan_id
        )

    except TimesheetPlanNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return TimesheetPlanResponse.model_validate(
        timesheet_plan
    )


# ============================================================
# GET BY EMPLOYEE
# ============================================================

@router.get(
    "/employee/{employee_id}",
    response_model=list[TimesheetPlanResponse],
)
def get_employee_timesheet_plans(
    employee_id: int,
    service: TimesheetPlanService = Depends(
        get_timesheet_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
) -> list[TimesheetPlanResponse]:

    try:
        timesheet_plans = service.get_by_employee_id(
            employee_id
        )

    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return [
        TimesheetPlanResponse.model_validate(
            timesheet_plan
        )
        for timesheet_plan in timesheet_plans
    ]


# ============================================================
# FIX MONTH
# ============================================================

@router.post(
    "/employee/{employee_id}/month/{year}/{month}/fix",
    response_model=list[TimesheetPlanResponse],
)
def fix_timesheet_month(
    employee_id: int,
    year: int,
    month: int,
    service: TimesheetPlanService = Depends(
        get_timesheet_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
) -> list[TimesheetPlanResponse]:

    try:
        timesheet_plans = service.fix_month(
            employee_id=employee_id,
            year=year,
            month=month,
        )

    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except TimesheetMonthAlreadyFixedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return [
        TimesheetPlanResponse.model_validate(
            timesheet_plan
        )
        for timesheet_plan in timesheet_plans
    ]


# ============================================================
# UPDATE
# ============================================================

@router.put(
    "/{timesheet_plan_id}",
    response_model=TimesheetPlanResponse,
)
def update_timesheet_plan(
    timesheet_plan_id: int,
    data: TimesheetPlanUpdate,
    service: TimesheetPlanService = Depends(
        get_timesheet_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
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

    except TimesheetPlanFixedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except TimesheetPlanAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return TimesheetPlanResponse.model_validate(
        timesheet_plan
    )


# ============================================================
# DELETE
# ============================================================

@router.delete(
    "/{timesheet_plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_timesheet_plan(
    timesheet_plan_id: int,
    service: TimesheetPlanService = Depends(
        get_timesheet_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
) -> Response:

    try:
        service.delete(
            timesheet_plan_id
        )

    except TimesheetPlanNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except TimesheetPlanFixedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )