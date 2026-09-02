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
    # Создаём фиктивный репозиторий планов.
    repository = Mock()

    # Создаём фиктивный сервис сотрудников.
    employee_service = Mock()

    # Сотрудник существует.
    employee_service.get_by_id.return_value = Mock(id=1)

    # В месяце уже есть зафиксированный план.
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

    # Создание плана в зафиксированном месяце
    # должно завершиться ошибкой.
    with pytest.raises(TimesheetMonthAlreadyFixedError):
        service.create(
            employee_id=1,
            work_date=date(2026, 9, 10),
            planned_hours=8,
        )


def test_create_duplicate_plan_for_same_date_is_forbidden():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Сотрудник существует.
    employee_service.get_by_id.return_value = Mock(id=1)

    # Месяц НЕ зафиксирован.
    repository.get_fixed_by_employee_and_date_range.return_value = []

    # Но на эту дату уже существует план.
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

    # Попытка создать второй план
    # на ту же дату должна вызвать ошибку.
    with pytest.raises(TimesheetPlanAlreadyExistsError):
        service.create(
            employee_id=1,
            work_date=date(2026, 9, 10),
            planned_hours=8,
        )


def test_create_plan_successfully():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Сотрудник существует.
    employee_service.get_by_id.return_value = Mock(id=1)

    # Месяц не зафиксирован.
    repository.get_fixed_by_employee_and_date_range.return_value = []

    # На эту дату плана ещё нет.
    repository.get_by_employee_and_date.return_value = None

    # Имитируем создание плана в репозитории.
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

    # Проверяем созданный план.
    assert result.id == 15
    assert result.employee_id == 1
    assert result.work_date == date(2026, 9, 10)
    assert result.planned_hours == 8
    assert result.is_fixed is False

    # Проверяем, что репозиторий действительно вызвали.
    repository.create.assert_called_once()


def test_update_fixed_plan_is_forbidden():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Создаём зафиксированный план.
    fixed_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=True,
    )

    # Репозиторий возвращает этот план.
    repository.get_by_id.return_value = fixed_plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    # Изменение зафиксированного плана
    # должно вызвать ошибку.
    with pytest.raises(TimesheetPlanFixedError):
        service.update(
            timesheet_plan_id=10,
            work_date=date(2026, 9, 11),
            planned_hours=7,
        )

    # План не должен был попасть в update().
    repository.update.assert_not_called()
def test_update_plan_to_existing_date_is_forbidden():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # План, который мы хотим изменить.
    current_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=False,
    )

    # Другой план этого же сотрудника,
    # который уже занимает новую дату.
    existing_plan = Mock(
        id=11,
        employee_id=1,
        work_date=date(2026, 9, 11),
        planned_hours=7,
        is_fixed=False,
    )

    # При поиске плана по ID возвращаем текущий план.
    repository.get_by_id.return_value = current_plan

    # При проверке новой даты возвращаем другой существующий план.
    repository.get_by_employee_and_date.return_value = existing_plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    # Пытаемся перенести План №10
    # на дату, которая уже занята Планом №11.
    with pytest.raises(TimesheetPlanAlreadyExistsError):
        service.update(
            timesheet_plan_id=10,
            work_date=date(2026, 9, 11),
            planned_hours=8,
        )

    # Изменение в репозитории происходить не должно.
    repository.update.assert_not_called()
def test_update_plan_successfully():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Существующий незакреплённый план.
    current_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=False,
    )

    # Репозиторий возвращает существующий план.
    repository.get_by_id.return_value = current_plan

    # Новая дата свободна.
    repository.get_by_employee_and_date.return_value = None

    # Репозиторий возвращает изменённый план.
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

    # Проверяем, что данные действительно изменились.
    assert result.id == 10
    assert result.employee_id == 1
    assert result.work_date == date(2026, 9, 12)
    assert result.planned_hours == 7
    assert result.is_fixed is False

    # Проверяем, что репозиторий вызвали.
    repository.update.assert_called_once_with(current_plan)
def test_delete_fixed_plan_is_forbidden():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Создаём зафиксированный план.
    fixed_plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=True,
    )

    # Репозиторий возвращает зафиксированный план.
    repository.get_by_id.return_value = fixed_plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    # Попытка удалить зафиксированный план
    # должна вызвать ошибку.
    with pytest.raises(TimesheetPlanFixedError):
        service.delete(
            timesheet_plan_id=10,
        )

    # Удаление в репозитории выполняться не должно.
    repository.delete.assert_not_called()

def test_delete_plan_successfully():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Создаём обычный, незакреплённый план.
    plan = Mock(
        id=10,
        employee_id=1,
        work_date=date(2026, 9, 10),
        planned_hours=8,
        is_fixed=False,
    )

    # Репозиторий возвращает существующий план.
    repository.get_by_id.return_value = plan

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    # Удаляем план.
    result = service.delete(
        timesheet_plan_id=10,
    )

    # Метод delete() ничего не должен возвращать.
    assert result is None

    # Проверяем, что репозиторий действительно вызвал удаление.
    repository.delete.assert_called_once_with(plan)
def test_fix_month_without_plans_returns_empty_list():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Сотрудник существует.
    employee_service.get_by_id.return_value = Mock(id=1)

    # В выбранном месяце нет ни одного плана.
    repository.get_by_employee_and_date_range.return_value = []

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    # Пытаемся зафиксировать месяц.
    result = service.fix_month(
        employee_id=1,
        year=2026,
        month=9,
    )

    # Если планов нет, возвращается пустой список.
    assert result == []

    # Ни один план не должен обновляться.
    repository.update.assert_not_called()
def test_fix_month_successfully():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Сотрудник существует.
    employee_service.get_by_id.return_value = Mock(id=1)

    # Создаём несколько планов одного сотрудника
    # за сентябрь 2026 года.
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

    # Репозиторий возвращает планы за месяц.
    repository.get_by_employee_and_date_range.return_value = plans

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    # Фиксируем сентябрь 2026 года.
    result = service.fix_month(
        employee_id=1,
        year=2026,
        month=9,
    )

    # Проверяем, что сервис вернул все планы.
    assert result == plans

    # Проверяем, что каждый план действительно зафиксирован.
    assert plan_1.is_fixed is True
    assert plan_2.is_fixed is True
    assert plan_3.is_fixed is True

    # Проверяем, что каждый план был передан
    # в repository.update().
    assert repository.update.call_count == 3

    repository.update.assert_any_call(plan_1)
    repository.update.assert_any_call(plan_2)
    repository.update.assert_any_call(plan_3)
def test_fix_already_fixed_month_is_forbidden():
    # Создаём фиктивные зависимости.
    repository = Mock()
    employee_service = Mock()

    # Сотрудник существует.
    employee_service.get_by_id.return_value = Mock(id=1)

    # Все планы месяца уже зафиксированы.
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

    # Репозиторий возвращает планы месяца.
    repository.get_by_employee_and_date_range.return_value = plans

    service = TimesheetPlanService(
        repository=repository,
        employee_service=employee_service,
    )

    # Повторная фиксация месяца должна вызвать ошибку.
    with pytest.raises(TimesheetMonthAlreadyFixedError):
        service.fix_month(
            employee_id=1,
            year=2026,
            month=9,
        )

    # Ни один план не должен обновляться.
    repository.update.assert_not_called()