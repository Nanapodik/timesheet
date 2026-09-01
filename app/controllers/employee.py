from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_employee_service
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.employee import EmployeeNotFoundError, EmployeeService
from app.services.organization import OrganizationNotFoundError


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    data: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponse:
    try:
        employee = service.create(
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            birth_date=data.birth_date,
            organization_id=data.organization_id,
            is_active=data.is_active,
        )
    except OrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return EmployeeResponse.model_validate(employee)


@router.get(
    "",
    response_model=list[EmployeeResponse],
)
def get_employees(
    service: EmployeeService = Depends(get_employee_service),
) -> list[EmployeeResponse]:
    employees = service.get_all()
    return [EmployeeResponse.model_validate(employee) for employee in employees]


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponse:
    employee = service.get_by_id(employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id={employee_id} not found",
        )

    return EmployeeResponse.model_validate(employee)


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponse:
    try:
        employee = service.update(
            employee_id=employee_id,
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            birth_date=data.birth_date,
            organization_id=data.organization_id,
            is_active=data.is_active,
        )
    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except OrganizationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return EmployeeResponse.model_validate(employee)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
) -> Response:
    try:
        service.delete(employee_id)
    except EmployeeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)