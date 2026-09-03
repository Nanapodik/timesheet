from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from app.services.timesheet_fact import (
    TimesheetFactAlreadyExistsError,
    TimesheetFactFutureDateError,
    TimesheetFactHoursMismatchError,
    TimesheetFactService,
    TimesheetPlanNotFoundForFactError,
)


def test_create_fact_for_future_date_is_forbidden():
    fact_repository = Mock()
    plan_repository = Mock()

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    future_date = date.today() + timedelta(days=1)

    with pytest.raises(TimesheetFactFutureDateError):
        service.create(
            employee_id=1,
            work_date=future_date,
            actual_hours=8,
        )

    plan_repository.get_by_employee_and_date.assert_not_called()
    fact_repository.create.assert_not_called()


def test_create_fact_when_actual_hours_less_than_plan_is_allowed():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    plan_repository.get_by_employee_and_date.return_value = plan
    fact_repository.get_by_employee_and_date.return_value = None

    def create_fact(fact):
        fact.id = 20
        return fact

    fact_repository.create.side_effect = create_fact

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    result = service.create(
        employee_id=1,
        work_date=work_date,
        actual_hours=7,
    )

    assert result.id == 20
    assert result.employee_id == 1
    assert result.work_date == work_date
    assert result.actual_hours == 7

    plan_repository.get_by_employee_and_date.assert_called_once_with(
        employee_id=1,
        work_date=work_date,
    )

    fact_repository.get_by_employee_and_date.assert_called_once_with(
        employee_id=1,
        work_date=work_date,
    )

    fact_repository.create.assert_called_once()


def test_create_fact_when_actual_hours_exceed_plan_is_forbidden():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    plan_repository.get_by_employee_and_date.return_value = plan

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    with pytest.raises(
        TimesheetFactHoursMismatchError,
        match="Actual hours cannot exceed planned hours: 8",
    ):
        service.create(
            employee_id=1,
            work_date=work_date,
            actual_hours=9,
        )

    fact_repository.get_by_employee_and_date.assert_not_called()
    fact_repository.create.assert_not_called()


def test_create_duplicate_fact_for_same_date_is_forbidden():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    plan_repository.get_by_employee_and_date.return_value = plan

    existing_fact = Mock(
        id=10,
        employee_id=1,
        work_date=work_date,
        actual_hours=8,
    )

    fact_repository.get_by_employee_and_date.return_value = (
        existing_fact
    )

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    with pytest.raises(TimesheetFactAlreadyExistsError):
        service.create(
            employee_id=1,
            work_date=work_date,
            actual_hours=8,
        )

    fact_repository.create.assert_not_called()


def test_create_fact_without_plan_is_forbidden():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    plan_repository.get_by_employee_and_date.return_value = None

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    with pytest.raises(
        TimesheetPlanNotFoundForFactError,
        match="Timesheet plan for employee 1",
    ):
        service.create(
            employee_id=1,
            work_date=work_date,
            actual_hours=8,
        )

    fact_repository.get_by_employee_and_date.assert_not_called()
    fact_repository.create.assert_not_called()


def test_create_fact_successfully():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    plan_repository.get_by_employee_and_date.return_value = plan
    fact_repository.get_by_employee_and_date.return_value = None

    def create_fact(fact):
        fact.id = 20
        return fact

    fact_repository.create.side_effect = create_fact

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    result = service.create(
        employee_id=1,
        work_date=work_date,
        actual_hours=8,
    )

    assert result.id == 20
    assert result.employee_id == 1
    assert result.work_date == work_date
    assert result.actual_hours == 8

    fact_repository.create.assert_called_once()


def test_update_fact_successfully():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    fact = Mock(
        id=10,
        employee_id=1,
        work_date=work_date,
        actual_hours=8,
    )

    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    fact_repository.get_by_id.return_value = fact
    plan_repository.get_by_employee_and_date.return_value = plan
    fact_repository.update.side_effect = lambda fact: fact

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    result = service.update(
        timesheet_fact_id=10,
        actual_hours=6,
    )

    assert result.actual_hours == 6

    plan_repository.get_by_employee_and_date.assert_called_once_with(
        employee_id=1,
        work_date=work_date,
    )

    fact_repository.update.assert_called_once_with(fact)


def test_update_fact_when_actual_hours_less_than_plan_is_allowed():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    fact = Mock(
        id=10,
        employee_id=1,
        work_date=work_date,
        actual_hours=8,
    )

    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    fact_repository.get_by_id.return_value = fact
    plan_repository.get_by_employee_and_date.return_value = plan

    # Repository update returns the modified object.
    fact_repository.update.side_effect = lambda fact: fact

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    result = service.update(
        timesheet_fact_id=10,
        actual_hours=3,
    )

    assert result.actual_hours == 3

    fact_repository.update.assert_called_once_with(fact)


def test_update_fact_when_actual_hours_exceed_plan_is_forbidden():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    fact = Mock(
        id=10,
        employee_id=1,
        work_date=work_date,
        actual_hours=8,
    )

    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    fact_repository.get_by_id.return_value = fact
    plan_repository.get_by_employee_and_date.return_value = plan

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    with pytest.raises(
        TimesheetFactHoursMismatchError,
        match="Actual hours cannot exceed planned hours: 8",
    ):
        service.update(
            timesheet_fact_id=10,
            actual_hours=9,
        )

    fact_repository.update.assert_not_called()


def test_update_fact_without_plan_is_forbidden():
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    fact = Mock(
        id=10,
        employee_id=1,
        work_date=work_date,
        actual_hours=8,
    )

    fact_repository.get_by_id.return_value = fact
    plan_repository.get_by_employee_and_date.return_value = None

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    with pytest.raises(
        TimesheetPlanNotFoundForFactError,
        match="Timesheet plan for employee 1",
    ):
        service.update(
            timesheet_fact_id=10,
            actual_hours=6,
        )

    fact_repository.update.assert_not_called()


def test_update_fact_for_future_date_is_forbidden():
    fact_repository = Mock()
    plan_repository = Mock()

    future_date = date.today() + timedelta(days=1)

    fact = Mock(
        id=10,
        employee_id=1,
        work_date=future_date,
        actual_hours=8,
    )

    fact_repository.get_by_id.return_value = fact

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    with pytest.raises(TimesheetFactFutureDateError):
        service.update(
            timesheet_fact_id=10,
            actual_hours=8,
        )

    plan_repository.get_by_employee_and_date.assert_not_called()
    fact_repository.update.assert_not_called()