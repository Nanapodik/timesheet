from calendar import monthrange
from datetime import date

from app.models.timesheet import TimesheetPlan
from app.repositories.timesheet import TimesheetPlanRepository
from app.services.employee import (
    EmployeeNotFoundError,
    EmployeeService,
)


class TimesheetPlanNotFoundError(Exception):
    """Timesheet plan was not found."""

    def __init__(self, timesheet_plan_id: int) -> None:
        self.timesheet_plan_id = timesheet_plan_id

        super().__init__(
            f"Timesheet plan with id={timesheet_plan_id} not found"
        )


class TimesheetPlanAlreadyExistsError(Exception):
    """Timesheet plan already exists for employee and date."""

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
    """Timesheet plan is fixed."""

    def __init__(
        self,
        timesheet_plan_id: int,
    ) -> None:
        self.timesheet_plan_id = timesheet_plan_id

        super().__init__(
            f"Timesheet plan with id={timesheet_plan_id} is fixed"
        )


class TimesheetMonthAlreadyFixedError(Exception):
    """Timesheet month is already fixed."""

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

        employee = self._employee_service.get_by_id(
            employee_id
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

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

        timesheet_plan = TimesheetPlan(
            employee_id=employee_id,
            work_date=work_date,
            planned_hours=planned_hours,
            is_fixed=False,
        )

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

        employee = self._employee_service.get_by_id(
            employee_id
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        if month < 1 or month > 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

        first_day = date(
            year,
            month,
            1,
        )

        last_day = date(
            year,
            month,
            monthrange(
                year,
                month,
            )[1],
        )

        plans = (
            self._repository
            .get_by_employee_and_date_range(
                employee_id=employee_id,
                start_date=first_day,
                end_date=last_day,
            )
        )

        if not plans:
            return []

        if all(plan.is_fixed for plan in plans):
            raise TimesheetMonthAlreadyFixedError(
                employee_id,
                year,
                month,
            )

        return self._repository.fix_month(
            plans
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

        timesheet_plan = self.get_by_id(
            timesheet_plan_id
        )

        if timesheet_plan.is_fixed:
            raise TimesheetPlanFixedError(
                timesheet_plan_id
            )

        employee_id = timesheet_plan.employee_id

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

        timesheet_plan.work_date = work_date
        timesheet_plan.planned_hours = planned_hours

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

        timesheet_plan = self.get_by_id(
            timesheet_plan_id
        )

        if timesheet_plan.is_fixed:
            raise TimesheetPlanFixedError(
                timesheet_plan_id
            )

        self._repository.delete(
            timesheet_plan
        )