from collections.abc import Generator

from app.database.connection import SessionLocal

from app.repositories.employee import EmployeeRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.timesheet import TimesheetPlanRepository
from app.repositories.timesheet_fact import TimesheetFactRepository
from app.repositories.user import UserRepository

from app.services.employee import EmployeeService
from app.services.organization import OrganizationService
from app.services.timesheet import TimesheetPlanService
from app.services.timesheet_fact import TimesheetFactService
from app.services.timesheet_report import TimesheetReportService
from app.services.user import UserService


def get_organization_service() -> Generator[
    OrganizationService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        yield OrganizationService(
            OrganizationRepository(session),
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
        employee_service = EmployeeService(
            EmployeeRepository(session),
        )

        yield TimesheetPlanService(
            TimesheetPlanRepository(session),
            employee_service,
        )
    finally:
        session.close()


def get_timesheet_fact_service() -> Generator[
    TimesheetFactService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        yield TimesheetFactService(
            TimesheetFactRepository(session),
            TimesheetPlanRepository(session),
        )
    finally:
        session.close()


def get_timesheet_report_service() -> Generator[
    TimesheetReportService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        yield TimesheetReportService(
            TimesheetPlanRepository(session),
            TimesheetFactRepository(session),
            EmployeeRepository(session),
        )
    finally:
        session.close()


def get_user_service() -> Generator[
    UserService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        yield UserService(
            UserRepository(session),
        )
    finally:
        session.close()