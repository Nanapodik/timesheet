import pytest

from fastapi.testclient import TestClient

from app.dependencies import (
    get_timesheet_fact_service,
    get_timesheet_service,
)
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def timesheet_service_mock():
    from unittest.mock import Mock

    return Mock()


@pytest.fixture
def client_with_timesheet_service(
    timesheet_service_mock,
):
    app.dependency_overrides[get_timesheet_service] = (
        lambda: timesheet_service_mock
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
):
    app.dependency_overrides[get_timesheet_fact_service] = (
        lambda: timesheet_fact_service_mock
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()