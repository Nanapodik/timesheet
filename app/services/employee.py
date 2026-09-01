from datetime import date

from app.models.employee import Employee
from app.repositories.employee import EmployeeRepository
from app.services.organization import OrganizationNotFoundError, OrganizationService


class EmployeeNotFoundError(Exception):
    def __init__(self, employee_id: int) -> None:
        self.employee_id = employee_id
        super().__init__(f"Employee with id={employee_id} not found")


class EmployeeService:
    def __init__(
        self,
        repository: EmployeeRepository,
        organization_service: OrganizationService,
    ) -> None:
        self._repository = repository
        self._organization_service = organization_service

    def create(
        self,
        first_name: str,
        last_name: str,
        middle_name: str,
        birth_date: date,
        organization_id: int,
        is_active: bool = True,
    ) -> Employee:
        self._ensure_organization(organization_id)
        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            birth_date=birth_date,
            organization_id=organization_id,
            is_active=is_active,
        )
        return self._repository.create(employee)

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self._repository.get_by_id(employee_id)

    def get_all(self) -> list[Employee]:
        return self._repository.get_all()

    def get_by_organization_id(self, organization_id: int) -> list[Employee]:
        self._ensure_organization(organization_id)
        return self._repository.get_by_organization_id(organization_id)

    def update(
        self,
        employee_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        middle_name: str | None = None,
        birth_date: date | None = None,
        organization_id: int | None = None,
        is_active: bool | None = None,
    ) -> Employee:
        employee = self._get_existing(employee_id)

        if organization_id is not None:
            self._ensure_organization(organization_id)
            employee.organization_id = organization_id
        if first_name is not None:
            employee.first_name = first_name
        if last_name is not None:
            employee.last_name = last_name
        if middle_name is not None:
            employee.middle_name = middle_name
        if birth_date is not None:
            employee.birth_date = birth_date
        if is_active is not None:
            employee.is_active = is_active

        return self._repository.update(employee)

    def delete(self, employee_id: int) -> None:
        employee = self._get_existing(employee_id)
        self._repository.delete(employee)

    def _get_existing(self, employee_id: int) -> Employee:
        employee = self._repository.get_by_id(employee_id)
        if employee is None:
            raise EmployeeNotFoundError(employee_id)
        return employee

    def _ensure_organization(self, organization_id: int) -> None:
        if self._organization_service.get_by_id(organization_id) is None:
            raise OrganizationNotFoundError(organization_id)
