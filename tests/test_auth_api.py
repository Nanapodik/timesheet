from unittest.mock import Mock

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.dependencies import (
    get_current_admin,
    get_current_user,
    get_employee_service,
    get_organization_service,
    get_timesheet_fact_service,
    get_timesheet_report_service,
)

from app.main import app

from app.models.user import User


# ============================================================
# BASIC ROLE CHECKS
# ============================================================

def test_admin_has_admin_access(test_user):
    test_user.role = "admin"

    result = get_current_admin(test_user)

    assert result is test_user


def test_regular_user_has_no_admin_access(test_user):
    test_user.role = "user"

    with pytest.raises(HTTPException) as error:
        get_current_admin(test_user)

    assert error.value.status_code == status.HTTP_403_FORBIDDEN
    assert error.value.detail == "Admin access required"


# ============================================================
# ORGANIZATIONS
# ============================================================

def test_regular_user_cannot_access_organizations(test_user):
    test_user.role = "user"

    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )

    try:
        with TestClient(app) as client:
            response = client.get("/organizations")

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Admin access required"
        }

    finally:
        app.dependency_overrides.clear()


def test_admin_can_access_organizations(test_user):
    test_user.role = "admin"

    organization_service = Mock()
    organization_service.get_all.return_value = []

    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )

    app.dependency_overrides[get_organization_service] = (
        lambda: organization_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/organizations")

        assert response.status_code == 200
        assert response.json() == []

        organization_service.get_all.assert_called_once()

    finally:
        app.dependency_overrides.clear()


# ============================================================
# EMPLOYEES
# ============================================================

def test_regular_user_cannot_access_employees(test_user):
    test_user.role = "user"

    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )

    try:
        with TestClient(app) as client:
            response = client.get("/employees")

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Admin access required"
        }

    finally:
        app.dependency_overrides.clear()


def test_admin_can_access_employees(test_user):
    test_user.role = "admin"

    employee_service = Mock()
    employee_service.get_all.return_value = []

    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )

    app.dependency_overrides[get_employee_service] = (
        lambda: employee_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/employees")

        assert response.status_code == 200
        assert response.json() == []

        employee_service.get_all.assert_called_once()

    finally:
        app.dependency_overrides.clear()


# ============================================================
# TIMESHEET FACTS
# ============================================================

def test_regular_user_cannot_access_timesheet_facts(test_user):
    test_user.role = "user"

    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )

    try:
        with TestClient(app) as client:
            response = client.get("/timesheet-facts")

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Admin access required"
        }

    finally:
        app.dependency_overrides.clear()


def test_admin_can_access_timesheet_facts(test_user):
    test_user.role = "admin"

    timesheet_fact_service = Mock()
    timesheet_fact_service.get_all.return_value = []

    app.dependency_overrides[get_current_admin] = (
        lambda: test_user
    )

    app.dependency_overrides[get_timesheet_fact_service] = (
        lambda: timesheet_fact_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/timesheet-facts")

        assert response.status_code == 200
        assert response.json() == []

        timesheet_fact_service.get_all.assert_called_once()

    finally:
        app.dependency_overrides.clear()


# ============================================================
# TIMESHEET REPORTS
# ============================================================

def test_regular_user_cannot_access_timesheet_reports(test_user):
    test_user.role = "user"

    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                "/timesheet-reports/employee/1/month/2026/8"
            )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Admin access required"
        }

    finally:
        app.dependency_overrides.clear()


def test_admin_can_access_timesheet_reports(test_user):
    test_user.role = "admin"

    timesheet_report_service = Mock()

    timesheet_report_service.get_month_report.return_value = {
        "employee_id": 1,
        "year": 2026,
        "month": 8,
        "planned_total": 176.0,
        "actual_total": 176.0,
        "difference": 0.0,
        "days": [],
    }

    app.dependency_overrides[get_current_admin] = (
        lambda: test_user
    )

    app.dependency_overrides[get_timesheet_report_service] = (
        lambda: timesheet_report_service
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                "/timesheet-reports/employee/1/month/2026/8"
            )

        assert response.status_code == 200

        assert response.json() == {
            "employee_id": 1,
            "year": 2026,
            "month": 8,
            "planned_total": 176.0,
            "actual_total": 176.0,
            "difference": 0.0,
            "days": [],
        }

        timesheet_report_service.get_month_report.assert_called_once_with(
            employee_id=1,
            year=2026,
            month=8,
        )

    finally:
        app.dependency_overrides.clear()