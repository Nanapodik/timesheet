from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, employee: Employee) -> Employee:
        self._session.add(employee)
        self._session.commit()
        self._session.refresh(employee)
        return employee

    def get_by_id(self, employee_id: int) -> Employee | None:
        statement = select(Employee).where(Employee.id == employee_id)
        return self._session.scalar(statement)

    def get_all(self) -> list[Employee]:
        statement = select(Employee)
        return list(self._session.scalars(statement).all())

    def get_by_organization_id(self, organization_id: int) -> list[Employee]:
        statement = select(Employee).where(Employee.organization_id == organization_id)
        return list(self._session.scalars(statement).all())

    def update(self, employee: Employee) -> Employee:
        self._session.commit()
        self._session.refresh(employee)
        return employee

    def delete(self, employee: Employee) -> None:
        self._session.delete(employee)
        self._session.commit()
