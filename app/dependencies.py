from collections.abc import Generator

from app.database.connection import SessionLocal

from app.repositories.employee import EmployeeRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.timesheet import TimesheetPlanRepository

from app.services.employee import EmployeeService
from app.services.organization import OrganizationService
from app.services.timesheet import TimesheetPlanService


def get_organization_service() -> Generator[
    OrganizationService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        yield OrganizationService(
            OrganizationRepository(session)
        )
    finally:
        session.close()


def get_employee_service() -> Generator[
    EmployeeService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        yield EmployeeService(
            EmployeeRepository(session),
            OrganizationService(
                OrganizationRepository(session)
            ),
        )
    finally:
        session.close()


def get_timesheet_service() -> Generator[
    TimesheetPlanService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        yield TimesheetPlanService(
            TimesheetPlanRepository(session),
            EmployeeService(
                EmployeeRepository(session),
                OrganizationService(
                    OrganizationRepository(session)
                ),
            ),
        )
    finally:
        session.close()