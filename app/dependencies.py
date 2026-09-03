from collections.abc import Generator

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database.connection import SessionLocal
from app.models.user import User

from app.repositories.employee import EmployeeRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.timesheet import TimesheetPlanRepository
from app.repositories.timesheet_fact import TimesheetFactRepository
from app.repositories.user import UserRepository

from app.security import decode_access_token

from app.services.employee import EmployeeService
from app.services.organization import OrganizationService
from app.services.timesheet import TimesheetPlanService
from app.services.timesheet_fact import TimesheetFactService
from app.services.timesheet_report import TimesheetReportService
from app.services.user import UserNotFoundError, UserService


security = HTTPBearer(
    auto_error=False
)


# ============================================================
# ORGANIZATION SERVICE
# ============================================================

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


# ============================================================
# EMPLOYEE SERVICE
# ============================================================

def get_employee_service() -> Generator[
    EmployeeService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        organization_service = OrganizationService(
            OrganizationRepository(session)
        )

        yield EmployeeService(
            EmployeeRepository(session),
            organization_service,
        )
    finally:
        session.close()


# ============================================================
# TIMESHEET PLAN SERVICE
# ============================================================

def get_timesheet_service() -> Generator[
    TimesheetPlanService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        employee_service = EmployeeService(
            EmployeeRepository(session),
            OrganizationService(
                OrganizationRepository(session)
            ),
        )

        yield TimesheetPlanService(
            TimesheetPlanRepository(session),
            employee_service,
        )
    finally:
        session.close()


# ============================================================
# TIMESHEET FACT SERVICE
# ============================================================

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


# ============================================================
# TIMESHEET REPORT SERVICE
# ============================================================

def get_timesheet_report_service() -> Generator[
    TimesheetReportService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        employee_service = EmployeeService(
            EmployeeRepository(session),
            OrganizationService(
                OrganizationRepository(session)
            ),
        )

        yield TimesheetReportService(
            TimesheetPlanRepository(session),
            TimesheetFactRepository(session),
            employee_service,
        )

    finally:
        session.close()


# ============================================================
# USER SERVICE
# ============================================================

def get_user_service() -> Generator[
    UserService,
    None,
    None,
]:
    session = SessionLocal()

    try:
        yield UserService(
            UserRepository(session)
        )
    finally:
        session.close()


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        security
    ),
    service: UserService = Depends(
        get_user_service
    ),
) -> User:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )

    try:
        user_id = decode_access_token(
            credentials.credentials
        )
    except (
        jwt.InvalidTokenError,
        ValueError,
    ) as error:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from error

    try:
        user = service.get_by_id(
            user_id
        )
    except UserNotFoundError as error:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        ) from error

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return user


# ============================================================
# CURRENT ADMIN
# ============================================================

def get_current_admin(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user