from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from app.services.timesheet_fact import (
    TimesheetFactAlreadyExistsError,
    TimesheetFactFutureDateError,
    TimesheetFactHoursMismatchError,
    TimesheetFactService,
)


def test_create_fact_for_future_date_is_forbidden():
    # Создаём фиктивные зависимости.
    fact_repository = Mock()
    plan_repository = Mock()

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    # Берём дату завтра.
    future_date = date.today() + timedelta(days=1)

    # Попытка создать факт за будущую дату
    # должна вызвать ошибку.
    with pytest.raises(TimesheetFactFutureDateError):
        service.create(
            employee_id=1,
            work_date=future_date,
            actual_hours=8,
        )

    # До репозитория дело доходить не должно.
    plan_repository.get_by_employee_id.assert_not_called()
    fact_repository.create.assert_not_called()


def test_create_fact_when_hours_do_not_match_plan_is_forbidden():
    # Создаём фиктивные зависимости.
    fact_repository = Mock()
    plan_repository = Mock()

    # План сотрудника.
    plan = Mock(
        id=1,
        employee_id=1,
        work_date=date.today(),
        planned_hours=8,
    )

    plan_repository.get_by_employee_id.return_value = [plan]

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    # В плане 8 часов, а пытаемся внести 7.
    with pytest.raises(TimesheetFactHoursMismatchError):
        service.create(
            employee_id=1,
            work_date=date.today(),
            actual_hours=7,
        )

    # Факт не должен создаваться.
    fact_repository.create.assert_not_called()


def test_create_duplicate_fact_for_same_date_is_forbidden():
    # Создаём фиктивные зависимости.
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    # План на эту дату.
    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    plan_repository.get_by_employee_id.return_value = [plan]

    # Факт на эту дату уже существует.
    existing_fact = Mock(
        id=10,
        employee_id=1,
        work_date=work_date,
        actual_hours=8,
    )

    fact_repository.get_by_employee_id.return_value = [
        existing_fact
    ]

    service = TimesheetFactService(
        timesheet_fact_repository=fact_repository,
        timesheet_plan_repository=plan_repository,
    )

    # Повторное создание факта должно вызвать ошибку.
    with pytest.raises(TimesheetFactAlreadyExistsError):
        service.create(
            employee_id=1,
            work_date=work_date,
            actual_hours=8,
        )

    # Новый факт не должен создаваться.
    fact_repository.create.assert_not_called()


def test_create_fact_successfully():
    # Создаём фиктивные зависимости.
    fact_repository = Mock()
    plan_repository = Mock()

    work_date = date.today()

    # План сотрудника.
    plan = Mock(
        id=1,
        employee_id=1,
        work_date=work_date,
        planned_hours=8,
    )

    plan_repository.get_by_employee_id.return_value = [plan]

    # Фактов на эту дату ещё нет.
    fact_repository.get_by_employee_id.return_value = []

    # Имитируем создание факта в репозитории.
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

    # Проверяем созданный факт.
    assert result.id == 20
    assert result.employee_id == 1
    assert result.work_date == work_date
    assert result.actual_hours == 8

    # Проверяем, что репозиторий действительно вызвали.
    fact_repository.create.assert_called_once()


def test_update_fact_for_future_date_is_forbidden():
    # Создаём фиктивные зависимости.
    fact_repository = Mock()
    plan_repository = Mock()

    future_date = date.today() + timedelta(days=1)

    # Существующий факт с будущей датой.
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

    # Изменение факта за будущую дату запрещено.
    with pytest.raises(TimesheetFactFutureDateError):
        service.update(
            timesheet_fact_id=10,
            actual_hours=8,
        )

    # План искать не должны.
    plan_repository.get_by_employee_id.assert_not_called()

    # Факт обновлять не должны.
    fact_repository.update.assert_not_called()