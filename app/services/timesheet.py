from calendar import monthrange
from datetime import date

from app.models.timesheet import TimesheetPlan
from app.repositories.timesheet import TimesheetPlanRepository
from app.services.employee import (
    EmployeeNotFoundError,
    EmployeeService,
)


class TimesheetPlanNotFoundError(Exception):

    def __init__(
        self,
        timesheet_plan_id: int,
    ) -> None:

        self.timesheet_plan_id = timesheet_plan_id

        super().__init__(
            f"Timesheet plan with id={timesheet_plan_id} not found"
        )


class TimesheetPlanAlreadyExistsError(Exception):

    def __init__(
        self,
        employee_id: int,
        work_date: date,
    ) -> None:

        self.employee_id = employee_id
        self.work_date = work_date

        super().__init__(
            f"Timesheet plan for employee {employee_id} "
            f"on {work_date} already exists"
        )


class TimesheetPlanFixedError(Exception):

    def __init__(
        self,
        timesheet_plan_id: int,
    ) -> None:

        self.timesheet_plan_id = timesheet_plan_id

        super().__init__(
            f"Timesheet plan with id={timesheet_plan_id} is fixed"
        )


class TimesheetMonthAlreadyFixedError(Exception):

    def __init__(
        self,
        employee_id: int,
        year: int,
        month: int,
    ) -> None:

        self.employee_id = employee_id
        self.year = year
        self.month = month

        super().__init__(
            f"Timesheet for employee {employee_id} "
            f"for {year}-{month:02d} is already fixed"
        )


class TimesheetPlanService:

    def __init__(
        self,
        repository: TimesheetPlanRepository,
        employee_service: EmployeeService,
    ) -> None:

        self._repository = repository
        self._employee_service = employee_service

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        employee_id: int,
        work_date: date,
        planned_hours: float,
    ) -> TimesheetPlan:

        # Проверяем существование сотрудника
        employee = self._employee_service.get_by_id(
            employee_id
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        # Определяем границы месяца
        first_day = date(
            work_date.year,
            work_date.month,
            1,
        )

        last_day = date(
            work_date.year,
            work_date.month,
            monthrange(
                work_date.year,
                work_date.month,
            )[1],
        )

        # Проверяем, не зафиксирован ли уже этот месяц
        fixed_plans = (
            self._repository
            .get_fixed_by_employee_and_date_range(
                employee_id=employee_id,
                start_date=first_day,
                end_date=last_day,
            )
        )

        if fixed_plans:
            raise TimesheetMonthAlreadyFixedError(
                employee_id,
                work_date.year,
                work_date.month,
            )

        # Проверяем наличие плана на эту дату
        existing_plan = (
            self._repository.get_by_employee_and_date(
                employee_id,
                work_date,
            )
        )

        if existing_plan is not None:
            raise TimesheetPlanAlreadyExistsError(
                employee_id,
                work_date,
            )

        # Создаём объект плана
        timesheet_plan = TimesheetPlan(
            employee_id=employee_id,
            work_date=work_date,
            planned_hours=planned_hours,
            is_fixed=False,
        )

        # Сохраняем
        return self._repository.create(
            timesheet_plan
        )

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        timesheet_plan_id: int,
    ) -> TimesheetPlan:

        timesheet_plan = self._repository.get_by_id(
            timesheet_plan_id
        )

        if timesheet_plan is None:
            raise TimesheetPlanNotFoundError(
                timesheet_plan_id
            )

        return timesheet_plan

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(self) -> list[TimesheetPlan]:

        return self._repository.get_all()

    # ========================================================
    # GET BY EMPLOYEE
    # ========================================================

    def get_by_employee_id(
        self,
        employee_id: int,
    ) -> list[TimesheetPlan]:

        # Проверяем сотрудника
        employee = self._employee_service.get_by_id(
            employee_id
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        return self._repository.get_by_employee_id(
            employee_id
        )

    # ========================================================
    # FIX MONTH
    # ========================================================

    def fix_month(
        self,
        employee_id: int,
        year: int,
        month: int,
    ) -> list[TimesheetPlan]:

        # Проверяем существование сотрудника
        employee = self._employee_service.get_by_id(
            employee_id
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        # Проверяем корректность месяца
        if month < 1 or month > 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

        # Первый день месяца
        first_day = date(
            year,
            month,
            1,
        )

        # Последний день месяца
        last_day = date(
            year,
            month,
            monthrange(year, month)[1],
        )

        # Получаем все планы сотрудника за месяц
        plans = (
            self._repository
            .get_by_employee_and_date_range(
                employee_id=employee_id,
                start_date=first_day,
                end_date=last_day,
            )
        )

        # Если планов нет, фиксировать нечего
        if not plans:
            return []

        # Проверяем, не зафиксирован ли месяц ранее
        if all(plan.is_fixed for plan in plans):
            raise TimesheetMonthAlreadyFixedError(
                employee_id,
                year,
                month,
            )

        # Фиксируем все планы месяца
        for plan in plans:
            plan.is_fixed = True

            self._repository.update(
                plan
            )

        return plans

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        timesheet_plan_id: int,
        work_date: date,
        planned_hours: float,
    ) -> TimesheetPlan:

        # Получаем существующий план
        timesheet_plan = self.get_by_id(
            timesheet_plan_id
        )

        # Нельзя изменять зафиксированный план
        if timesheet_plan.is_fixed:
            raise TimesheetPlanFixedError(
                timesheet_plan_id
            )

        # Сотрудника не меняем
        employee_id = timesheet_plan.employee_id

        # Проверяем, не занята ли новая дата
        # другим планом этого же сотрудника
        existing_plan = (
            self._repository.get_by_employee_and_date(
                employee_id,
                work_date,
            )
        )

        if (
            existing_plan is not None
            and existing_plan.id != timesheet_plan_id
        ):
            raise TimesheetPlanAlreadyExistsError(
                employee_id,
                work_date,
            )

        # Изменяем данные
        timesheet_plan.work_date = work_date
        timesheet_plan.planned_hours = planned_hours

        # Сохраняем
        return self._repository.update(
            timesheet_plan
        )

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        timesheet_plan_id: int,
    ) -> None:

        # Получаем существующий план
        timesheet_plan = self.get_by_id(
            timesheet_plan_id
        )

        # Нельзя удалить зафиксированный план
        if timesheet_plan.is_fixed:
            raise TimesheetPlanFixedError(
                timesheet_plan_id
            )

        self._repository.delete(
            timesheet_plan
        )