from datetime import date

from app.models.timesheet_fact import TimesheetFact
from app.repositories.timesheet import TimesheetPlanRepository
from app.repositories.timesheet_fact import TimesheetFactRepository


class TimesheetFactNotFoundError(Exception):
    """Timesheet fact was not found."""

    def __init__(
        self,
        timesheet_fact_id: int,
    ) -> None:
        super().__init__(
            f"Timesheet fact with id={timesheet_fact_id} not found"
        )


class TimesheetFactAlreadyExistsError(Exception):
    """Timesheet fact already exists for employee and date."""

    def __init__(
        self,
        employee_id: int,
        work_date: date,
    ) -> None:
        super().__init__(
            f"Timesheet fact for employee {employee_id} "
            f"on {work_date} already exists"
        )


class TimesheetFactFutureDateError(Exception):
    """Cannot create or update fact for a future date."""

    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(message)


class TimesheetFactHoursMismatchError(Exception):
    """Actual hours cannot exceed planned hours."""

    def __init__(
        self,
        planned_hours: float,
    ) -> None:
        super().__init__(
            f"Actual hours cannot exceed planned hours: {planned_hours}"
        )


class TimesheetPlanNotFoundForFactError(Exception):
    """Timesheet plan was not found for employee and date."""

    def __init__(
        self,
        employee_id: int,
        work_date: date,
    ) -> None:
        super().__init__(
            f"Timesheet plan for employee {employee_id} "
            f"on {work_date} not found"
        )


class TimesheetFactService:

    def __init__(
        self,
        timesheet_fact_repository: TimesheetFactRepository,
        timesheet_plan_repository: TimesheetPlanRepository,
    ) -> None:
        self._timesheet_fact_repository = (
            timesheet_fact_repository
        )

        self._timesheet_plan_repository = (
            timesheet_plan_repository
        )

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        employee_id: int,
        work_date: date,
        actual_hours: float,
    ) -> TimesheetFact:

        # Нельзя вводить факт за будущую дату.
        if work_date > date.today():
            raise TimesheetFactFutureDateError(
                "Cannot enter actual hours for a future date"
            )

        # Получаем план сотрудника на указанную дату.
        plan = (
            self._timesheet_plan_repository
            .get_by_employee_and_date(
                employee_id=employee_id,
                work_date=work_date,
            )
        )

        # Без плана нельзя создать факт.
        if plan is None:
            raise TimesheetPlanNotFoundForFactError(
                employee_id=employee_id,
                work_date=work_date,
            )

        # Бизнес-правило:
        # 0 <= actual_hours <= planned_hours
        if (
            actual_hours < 0
            or actual_hours > plan.planned_hours
        ):
            raise TimesheetFactHoursMismatchError(
                plan.planned_hours
            )

        # Проверяем, нет ли уже факта
        # для этого сотрудника и этой даты.
        existing_fact = (
            self._timesheet_fact_repository
            .get_by_employee_and_date(
                employee_id=employee_id,
                work_date=work_date,
            )
        )

        if existing_fact is not None:
            raise TimesheetFactAlreadyExistsError(
                employee_id=employee_id,
                work_date=work_date,
            )

        # Создаём факт.
        timesheet_fact = TimesheetFact(
            employee_id=employee_id,
            work_date=work_date,
            actual_hours=actual_hours,
        )

        return self._timesheet_fact_repository.create(
            timesheet_fact
        )

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        timesheet_fact_id: int,
    ) -> TimesheetFact:

        timesheet_fact = (
            self._timesheet_fact_repository
            .get_by_id(
                timesheet_fact_id
            )
        )

        if timesheet_fact is None:
            raise TimesheetFactNotFoundError(
                timesheet_fact_id
            )

        return timesheet_fact

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(self) -> list[TimesheetFact]:

        return self._timesheet_fact_repository.get_all()

    # ========================================================
    # GET BY EMPLOYEE
    # ========================================================

    def get_by_employee_id(
        self,
        employee_id: int,
    ) -> list[TimesheetFact]:

        return self._timesheet_fact_repository.get_by_employee_id(
            employee_id
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        timesheet_fact_id: int,
        actual_hours: float,
    ) -> TimesheetFact:

        # Получаем существующий факт.
        timesheet_fact = self.get_by_id(
            timesheet_fact_id
        )

        # Нельзя изменять факт за будущую дату.
        if timesheet_fact.work_date > date.today():
            raise TimesheetFactFutureDateError(
                "Cannot update actual hours for a future date"
            )

        # Получаем план сотрудника
        # на дату факта.
        plan = (
            self._timesheet_plan_repository
            .get_by_employee_and_date(
                employee_id=timesheet_fact.employee_id,
                work_date=timesheet_fact.work_date,
            )
        )

        # План должен существовать.
        if plan is None:
            raise TimesheetPlanNotFoundForFactError(
                employee_id=timesheet_fact.employee_id,
                work_date=timesheet_fact.work_date,
            )

        # Бизнес-правило:
        # 0 <= actual_hours <= planned_hours
        if (
            actual_hours < 0
            or actual_hours > plan.planned_hours
        ):
            raise TimesheetFactHoursMismatchError(
                plan.planned_hours
            )

        # Обновляем фактические часы.
        timesheet_fact.actual_hours = actual_hours

        return self._timesheet_fact_repository.update(
            timesheet_fact
        )

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        timesheet_fact_id: int,
    ) -> None:

        timesheet_fact = self.get_by_id(
            timesheet_fact_id
        )

        self._timesheet_fact_repository.delete(
            timesheet_fact
        )