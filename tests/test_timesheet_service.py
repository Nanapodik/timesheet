from datetime import date
from unittest.mock import Mock

import pytest

from app.services.timesheet import (
    TimesheetMonthAlreadyFixedError,
    TimesheetPlanAlreadyExistsError,
    TimesheetPlanFixedError,
    TimesheetPlanService,
)


def test_create_plan_for_fixed_month_is_forbidden():
    repository = Mock()
    employee_service = Mock()

    employee_service.get_by_id.return_value = Mock(id=1)

    repository.get_fixed_by_employee_and_date_range.return_value = [
        Mock(
            id=1,
            employee_id=1,
            work_date=date(2026, 9, 1),
            planned_hours=8,
            is_fixed=True,
        )
    ]

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    with pytest.raises(TimesheetMonthAlreadyFixedError):
        service.create(
            employee_id=1,
            work_date=date(2026, 9, 10),
            planned_hours=8,
        )


def test_create_duplicate_plan_for_same_date_is_forbidden():
    repository = Mock()
    employee_service = Mock()

    employee_service.get_by_id.return_value = Mock(id=1)

    repository.get_fixed_by_employee_and_date_range.return_value = []

    repository.get_by_employee_and_date.return_value = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=False,
    )

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    with pytest.raises(TimesheetPlanAlreadyExistsError):
        service.create(
            employee_id=1,
            work_date=date(2026, 9, 10),
            planned_hours=8,
        )


def test_create_plan_successfully():
    repository = Mock()
    employee_service = Mock()

    employee_service.get_by_id.return_value = Mock(id=1)

    repository.get_fixed_by_employee_and_date_range.return_value = []

    repository.get_by_employee_and_date.return_value = None

    def create_plan(plan):
        plan.id = 15
        return plan

    repository.create.side_effect = create_plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    result = service.create(
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
    )

    assert result.id == 15
    assert result.employee_id == 1
    assert result.work_date == date(2026, 9, 10)
    assert result.planned_hours == 8
    assert result.is_fixed is False

    repository.create.assert_called_once()


def test_update_fixed_plan_is_forbidden():
    repository = Mock()
    employee_service = Mock()

    fixed_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=True,
    )

    repository.get_by_id.return_value = fixed_plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    with pytest.raises(TimesheetPlanFixedError):
        service.update(
            timesheet_plan_id=10,
            work_date=date(2026, 9, 11),
            planned_hours=7,
        )

    repository.update.assert_not_called()


def test_update_plan_to_existing_date_is_forbidden():
    repository = Mock()
    employee_service = Mock()

    current_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=False,
    )

    existing_plan = Mock(
        id=11,
        employee_id=1,
        work_date=date(2026, 9, 11),
        planned_hours=7,
        is_fixed=False,
    )

    repository.get_by_id.return_value = current_plan

    repository.get_by_employee_and_date.return_value = existing_plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    with pytest.raises(TimesheetPlanAlreadyExistsError):
        service.update(
            timesheet_plan_id=10,
            work_date=date(2026, 9, 11),
            planned_hours=8,
        )

    repository.update.assert_not_called()


def test_update_plan_successfully():
    repository = Mock()
    employee_service = Mock()

    current_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=False,
    )

    repository.get_by_id.return_value = current_plan

    repository.get_by_employee_and_date.return_value = None

    repository.get_fixed_by_employee_and_date_range.return_value = []

    repository.update.return_value = current_plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    result = service.update(
        timesheet_plan_id=10,
        work_date=date(2026, 9, 12),
        planned_hours=7,
    )

    assert result.id == 10
    assert result.employee_id == 1
    assert result.work_date == date(2026, 9, 12)
    assert result.planned_hours == 7
    assert result.is_fixed is False

    repository.update.assert_called_once_with(
        current_plan
    )


def test_update_plan_to_fixed_month_is_forbidden():
    repository = Mock()
    employee_service = Mock()

    current_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 8, 10),
        planned_hours=8,
        is_fixed=False,
    )

    repository.get_by_id.return_value = current_plan

    repository.get_by_employee_and_date.return_value = None

    repository.get_fixed_by_employee_and_date_range.return_value = [
        Mock(
            id=20,
            employee_id=1,
            work_date=date(2026, 9, 1),
            planned_hours=8,
            is_fixed=True,
        )
    ]

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    with pytest.raises(TimesheetMonthAlreadyFixedError):
        service.update(
            timesheet_plan_id=10,
            work_date=date(2026, 9, 12),
            planned_hours=7,
        )

    repository.update.assert_not_called()


def test_delete_fixed_plan_is_forbidden():
    repository = Mock()
    employee_service = Mock()

    fixed_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=True,
    )

    repository.get_by_id.return_value = fixed_plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    with pytest.raises(TimesheetPlanFixedError):
        service.delete(
            timesheet_plan_id=10,
        )

    repository.delete.assert_not_called()


def test_delete_plan_successfully():
    repository = Mock()
    employee_service = Mock()

    plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=False,
    )

    repository.get_by_id.return_value = plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    result = service.delete(
        timesheet_plan_id=10,
    )

    assert result is None

    repository.delete.assert_called_once_with(plan)


def test_fix_month_without_plans_returns_empty_list():
    repository = Mock()
    employee_service = Mock()

    employee_service.get_by_id.return_value = Mock(id=1)

    repository.get_by_employee_and_date_range.return_value = []

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    result = service.fix_month(
        employee_id=1,
        year=2026,
        month=9,
    )

    assert result == []

    repository.fix_month.assert_not_called()


def test_fix_month_successfully():
    repository = Mock()
    employee_service = Mock()

    employee_service.get_by_id.return_value = Mock(id=1)

    plan_1 = Mock(
        id=1,
        employee_id=1,
        work_date=date(2026, 9, 1),
        planned_hours=8,
        is_fixed=False,
    )

    plan_2 = Mock(
        id=2,
        employee_id=1,
        work_date=date(2026, 9, 2),
        planned_hours=7,
        is_fixed=False,
    )

    plan_3 = Mock(
        id=3,
        employee_id=1,
        work_date=date(2026, 9, 3),
        planned_hours=8,
        is_fixed=False,
    )

    plans = [
        plan_1,
        plan_2,
        plan_3,
    ]

    repository.get_by_employee_and_date_range.return_value = plans
    repository.fix_month.return_value = plans

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    result = service.fix_month(
        employee_id=1,
        year=2026,
        month=9,
    )

    assert result == plans

    repository.fix_month.assert_called_once_with(
        plans
    )


def test_fix_already_fixed_month_is_forbidden():
    repository = Mock()
    employee_service = Mock()

    employee_service.get_by_id.return_value = Mock(id=1)

    plans = [
        Mock(
            id=1,
            employee_id=1,
            work_date=date(2026, 9, 1),
            planned_hours=8,
            is_fixed=True,
        ),
        Mock(
            id=2,
            employee_id=1,
            work_date=date(2026, 9, 2),
            planned_hours=7,
            is_fixed=True,
        ),
        Mock(
            id=3,
            employee_id=1,
            work_date=date(2026, 9, 3),
            planned_hours=8,
            is_fixed=True,
        ),
    ]

    repository.get_by_employee_and_date_range.return_value = plans

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    with pytest.raises(TimesheetMonthAlreadyFixedError):
        service.fix_month(
            employee_id=1,
            year=2026,
            month=9,
        )

    repository.fix_month.assert_not_called()