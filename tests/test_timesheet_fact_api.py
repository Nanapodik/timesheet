from datetime import date

from app.services.timesheet_fact import (
    TimesheetFactAlreadyExistsError,
    TimesheetFactFutureDateError,
    TimesheetFactHoursMismatchError,
    TimesheetFactNotFoundError,
)


def test_create_timesheet_fact_successfully(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    fact = type(
        "TimesheetFact",
        (),
        {
            "id": 1,
            "employee_id": 1,
            "work_date": date(2026, 9, 1),
            "actual_hours": 8,
        },
    )()

    timesheet_fact_service_mock.create.return_value = fact

    response = client_with_timesheet_fact_service.post(
        "/timesheet-facts",
        json={
            "employee_id": 1,
            "work_date": "2026-09-01",
            "actual_hours": 8,
        },
    )

    assert response.status_code == 201

    assert response.json() == {
        "id": 1,
        "employee_id": 1,
        "work_date": "2026-09-01",
        "actual_hours": 8,
    }

    timesheet_fact_service_mock.create.assert_called_once_with(
        employee_id=1,
        work_date=date(2026, 9, 1),
        actual_hours=8,
    )


def test_create_duplicate_timesheet_fact(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    timesheet_fact_service_mock.create.side_effect = (
        TimesheetFactAlreadyExistsError(
            1,
            date(2026, 9, 1),
        )
    )

    response = client_with_timesheet_fact_service.post(
        "/timesheet-facts",
        json={
            "employee_id": 1,
            "work_date": "2026-09-01",
            "actual_hours": 8,
        },
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Timesheet fact for employee 1 on "
            "2026-09-01 already exists"
        )
    }


def test_create_future_timesheet_fact(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    timesheet_fact_service_mock.create.side_effect = (
        TimesheetFactFutureDateError(
            "Cannot enter actual hours for a future date"
        )
    )

    response = client_with_timesheet_fact_service.post(
        "/timesheet-facts",
        json={
            "employee_id": 1,
            "work_date": "2026-09-10",
            "actual_hours": 8,
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "Cannot enter actual hours for a future date"
        )
    }


def test_create_timesheet_fact_hours_mismatch(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    timesheet_fact_service_mock.create.side_effect = (
        TimesheetFactHoursMismatchError(7)
    )

    response = client_with_timesheet_fact_service.post(
        "/timesheet-facts",
        json={
            "employee_id": 1,
            "work_date": "2026-09-01",
            "actual_hours": 8,
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "Actual hours must equal planned hours: 7"
        )
    }


def test_get_timesheet_fact_successfully(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    fact = type(
        "TimesheetFact",
        (),
        {
            "id": 1,
            "employee_id": 1,
            "work_date": date(2026, 9, 1),
            "actual_hours": 8,
        },
    )()

    timesheet_fact_service_mock.get_by_id.return_value = fact

    response = client_with_timesheet_fact_service.get(
        "/timesheet-facts/1"
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "employee_id": 1,
        "work_date": "2026-09-01",
        "actual_hours": 8,
    }

    timesheet_fact_service_mock.get_by_id.assert_called_once_with(1)


def test_get_timesheet_fact_not_found(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    timesheet_fact_service_mock.get_by_id.side_effect = (
        TimesheetFactNotFoundError(999)
    )

    response = client_with_timesheet_fact_service.get(
        "/timesheet-facts/999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Timesheet fact with id=999 not found"
    }


def test_get_all_timesheet_facts(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    fact = type(
        "TimesheetFact",
        (),
        {
            "id": 1,
            "employee_id": 1,
            "work_date": date(2026, 9, 1),
            "actual_hours": 8,
        },
    )()

    timesheet_fact_service_mock.get_all.return_value = [fact]

    response = client_with_timesheet_fact_service.get(
        "/timesheet-facts"
    )

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": 1,
            "employee_id": 1,
            "work_date": "2026-09-01",
            "actual_hours": 8,
        }
    ]

    timesheet_fact_service_mock.get_all.assert_called_once_with()


def test_get_employee_timesheet_facts(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    fact = type(
        "TimesheetFact",
        (),
        {
            "id": 1,
            "employee_id": 1,
            "work_date": date(2026, 9, 1),
            "actual_hours": 8,
        },
    )()

    timesheet_fact_service_mock.get_by_employee_id.return_value = [
        fact
    ]

    response = client_with_timesheet_fact_service.get(
        "/timesheet-facts/employee/1"
    )

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": 1,
            "employee_id": 1,
            "work_date": "2026-09-01",
            "actual_hours": 8,
        }
    ]

    timesheet_fact_service_mock.get_by_employee_id.assert_called_once_with(
        1
    )


def test_update_timesheet_fact_successfully(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    fact = type(
        "TimesheetFact",
        (),
        {
            "id": 1,
            "employee_id": 1,
            "work_date": date(2026, 9, 1),
            "actual_hours": 7,
        },
    )()

    timesheet_fact_service_mock.update.return_value = fact

    response = client_with_timesheet_fact_service.put(
        "/timesheet-facts/1",
        json={
            "actual_hours": 7,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "employee_id": 1,
        "work_date": "2026-09-01",
        "actual_hours": 7,
    }

    timesheet_fact_service_mock.update.assert_called_once_with(
        timesheet_fact_id=1,
        actual_hours=7,
    )


def test_update_timesheet_fact_not_found(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    timesheet_fact_service_mock.update.side_effect = (
        TimesheetFactNotFoundError(999)
    )

    response = client_with_timesheet_fact_service.put(
        "/timesheet-facts/999",
        json={
            "actual_hours": 8,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Timesheet fact with id=999 not found"
    }


def test_update_timesheet_fact_hours_mismatch(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    timesheet_fact_service_mock.update.side_effect = (
        TimesheetFactHoursMismatchError(8)
    )

    response = client_with_timesheet_fact_service.put(
        "/timesheet-facts/1",
        json={
            "actual_hours": 7,
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "Actual hours must equal planned hours: 8"
        )
    }


def test_delete_timesheet_fact_successfully(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    response = client_with_timesheet_fact_service.delete(
        "/timesheet-facts/1"
    )

    assert response.status_code == 204
    assert response.content == b""

    timesheet_fact_service_mock.delete.assert_called_once_with(1)


def test_delete_timesheet_fact_not_found(
    client_with_timesheet_fact_service,
    timesheet_fact_service_mock,
):
    timesheet_fact_service_mock.delete.side_effect = (
        TimesheetFactNotFoundError(999)
    )

    response = client_with_timesheet_fact_service.delete(
        "/timesheet-facts/999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Timesheet fact with id=999 not found"
    }


def test_create_timesheet_fact_with_negative_hours(
    client_with_timesheet_fact_service,
):
    response = client_with_timesheet_fact_service.post(
        "/timesheet-facts",
        json={
            "employee_id": 1,
            "work_date": "2026-09-01",
            "actual_hours": -1,
        },
    )

    assert response.status_code == 422


def test_create_timesheet_fact_with_more_than_24_hours(
    client_with_timesheet_fact_service,
):
    response = client_with_timesheet_fact_service.post(
        "/timesheet-facts",
        json={
            "employee_id": 1,
            "work_date": "2026-09-01",
            "actual_hours": 25,
        },
    )

    assert response.status_code == 422


def test_update_timesheet_fact_with_negative_hours(
    client_with_timesheet_fact_service,
):
    response = client_with_timesheet_fact_service.put(
        "/timesheet-facts/1",
        json={
            "actual_hours": -1,
        },
    )

    assert response.status_code == 422


def test_update_timesheet_fact_with_more_than_24_hours(
    client_with_timesheet_fact_service,
):
    response = client_with_timesheet_fact_service.put(
        "/timesheet-facts/1",
        json={
            "actual_hours": 25,
        },
    )

    assert response.status_code == 422