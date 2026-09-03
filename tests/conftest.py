import pytest

from fastapi.testclient import TestClient

from app.dependencies import (
    get_current_admin,
    get_current_user,
    get_timesheet_fact_service,
    get_timesheet_service,
)
from app.main import app

from app.models.user import User


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="test_user",
        password_hash="test_password_hash",
        is_active=True,
        role="user",
    )


@pytest.fixture
def admin_user():
    return User(
        id=2,
        username="admin_user",
        password_hash="admin_password_hash",
        is_active=True,
        role="admin",
    )


@pytest.fixture
def authenticated_client(test_user):
    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(admin_user):
    app.dependency_overrides[get_current_admin] = (
        lambda: admin_user
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def timesheet_service_mock():
    from unittest.mock import Mock

    return Mock()


@pytest.fixture
def client_with_timesheet_service(
    timesheet_service_mock,
    admin_user,
):
    app.dependency_overrides[get_timesheet_service] = (
        lambda: timesheet_service_mock
    )

    app.dependency_overrides[get_current_admin] = (
        lambda: admin_user
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def timesheet_fact_service_mock():
    from unittest.mock import Mock

    return Mock()


@pytest.fixture
def client_with_timesheet_fact_service(
    timesheet_fact_service_mock,
    admin_user,
):
    app.dependency_overrides[get_timesheet_fact_service] = (
        lambda: timesheet_fact_service_mock
    )

    app.dependency_overrides[get_current_admin] = (
        lambda: admin_user
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()