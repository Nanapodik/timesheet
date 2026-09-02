from datetime import date

from app.services.employee import EmployeeNotFoundError
from app.services.timesheet import (
    TimesheetMonthAlreadyFixedError,
    TimesheetPlanAlreadyExistsError,
    TimesheetPlanFixedError,
    TimesheetPlanNotFoundError,
)


def test_create_timesheet_plan_successfully(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    plan = type(
        "TimesheetPlan",
        (),
        {
            "id": 1,
            "employee_id": 1,
            "work_date": date(2026, 9, 1),
            "planned_hours": 8,
            "is_fixed": False,
        },
    )()

    timesheet_service_mock.create.return_value = plan

    response = client_with_timesheet_service.post(
        "/timesheet-plans",
        json={
            "employee_id": 1,
            "work_date": "2026-09-01",
            "planned_hours": 8,
        },
    )

    assert response.status_code == 201

    assert response.json() == {
        "id": 1,
        "employee_id": 1,
        "work_date": "2026-09-01",
        "planned_hours": 8,
        "is_fixed": False,
    }

    timesheet_service_mock.create.assert_called_once_with(
        employee_id=1,
        work_date=date(2026, 9, 1),
        planned_hours=8,
    )


def test_create_timesheet_plan_when_employee_not_found(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    timesheet_service_mock.create.side_effect = (
        EmployeeNotFoundError(999)
    )

    response = client_with_timesheet_service.post(
        "/timesheet-plans",
        json={
            "employee_id": 999,
            "work_date": "2026-09-01",
            "planned_hours": 8,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Employee with id=999 not found"
    }


def test_create_duplicate_timesheet_plan(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    timesheet_service_mock.create.side_effect = (
        TimesheetPlanAlreadyExistsError(
            1,
            date(2026, 9, 1),
        )
    )

    response = client_with_timesheet_service.post(
        "/timesheet-plans",
        json={
            "employee_id": 1,
            "work_date": "2026-09-01",
            "planned_hours": 8,
        },
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Timesheet plan for employee 1 on "
            "2026-09-01 already exists"
        )
    }


def test_get_timesheet_plan_successfully(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    plan = type(
        "TimesheetPlan",
        (),
        {
            "id": 1,
            "employee_id": 1,
            "work_date": date(2026, 9, 1),
            "planned_hours": 8,
            "is_fixed": False,
        },
    )()

    timesheet_service_mock.get_by_id.return_value = plan

    response = client_with_timesheet_service.get(
        "/timesheet-plans/1"
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "employee_id": 1,
        "work_date": "2026-09-01",
        "planned_hours": 8,
        "is_fixed": False,
    }

    timesheet_service_mock.get_by_id.assert_called_once_with(1)


def test_get_timesheet_plan_not_found(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    timesheet_service_mock.get_by_id.side_effect = (
        TimesheetPlanNotFoundError(999)
    )

    response = client_with_timesheet_service.get(
        "/timesheet-plans/999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Timesheet plan with id=999 not found"
    }


def test_update_fixed_timesheet_plan(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    timesheet_service_mock.update.side_effect = (
        TimesheetPlanFixedError(1)
    )

    response = client_with_timesheet_service.put(
        "/timesheet-plans/1",
        json={
            "work_date": "2026-09-01",
            "planned_hours": 8,
        },
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": "Timesheet plan with id=1 is fixed"
    }


def test_fix_month_successfully(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    plan = type(
        "TimesheetPlan",
        (),
        {
            "id": 1,
            "employee_id": 1,
            "work_date": date(2026, 9, 1),
            "planned_hours": 8,
            "is_fixed": True,
        },
    )()

    timesheet_service_mock.fix_month.return_value = [plan]

    response = client_with_timesheet_service.post(
        "/timesheet-plans/employee/1/month/2026/9/fix"
    )

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": 1,
            "employee_id": 1,
            "work_date": "2026-09-01",
            "planned_hours": 8,
            "is_fixed": True,
        }
    ]

    timesheet_service_mock.fix_month.assert_called_once_with(
        employee_id=1,
        year=2026,
        month=9,
    )


def test_fix_already_fixed_month(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    timesheet_service_mock.fix_month.side_effect = (
        TimesheetMonthAlreadyFixedError(
            1,
            2026,
            9,
        )
    )

    response = client_with_timesheet_service.post(
        "/timesheet-plans/employee/1/month/2026/9/fix"
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Timesheet for employee 1 for "
            "2026-09 is already fixed"
        )
    }


def test_delete_timesheet_plan_successfully(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    response = client_with_timesheet_service.delete(
        "/timesheet-plans/1"
    )

    assert response.status_code == 204
    assert response.content == b""

    timesheet_service_mock.delete.assert_called_once_with(1)


def test_delete_fixed_timesheet_plan(
    client_with_timesheet_service,
    timesheet_service_mock,
):
    timesheet_service_mock.delete.side_effect = (
        TimesheetPlanFixedError(1)
    )

    response = client_with_timesheet_service.delete(
        "/timesheet-plans/1"
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": "Timesheet plan with id=1 is fixed"
    }