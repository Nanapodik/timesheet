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

        # Создаём объект
        timesheet_plan = TimesheetPlan(
            employee_id=employee_id,
            work_date=work_date,
            planned_hours=planned_hours,
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

        # Сотрудника не меняем.
        # Берём employee_id из существующего плана.
        employee_id = timesheet_plan.employee_id

        # Проверяем, не занята ли новая дата
        # другим планом этого же сотрудника.
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

        # get_by_id сам выбросит 404-ошибку,
        # если такого плана нет.
        timesheet_plan = self.get_by_id(
            timesheet_plan_id
        )

        self._repository.delete(
            timesheet_plan
        )