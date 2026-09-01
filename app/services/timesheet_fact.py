from datetime import date

from app.models.timesheet_fact import TimesheetFact
from app.repositories.timesheet import TimesheetPlanRepository
from app.repositories.timesheet_fact import TimesheetFactRepository


class TimesheetFactNotFoundError(Exception):
    """Timesheet fact was not found."""


class TimesheetFactAlreadyExistsError(Exception):
    """Timesheet fact already exists for employee and date."""


class TimesheetFactFutureDateError(Exception):
    """Cannot create or update fact for a future date."""


class TimesheetFactHoursMismatchError(Exception):
    """Actual hours do not match planned hours."""


class TimesheetFactService:
    def __init__(
        self,
        timesheet_fact_repository: TimesheetFactRepository,
        timesheet_plan_repository: TimesheetPlanRepository,
    ) -> None:
        self._timesheet_fact_repository = timesheet_fact_repository
        self._timesheet_plan_repository = timesheet_plan_repository

    def create(
        self,
        employee_id: int,
        work_date: date,
        actual_hours: float,
    ) -> TimesheetFact:
        # Нельзя вносить факт за будущую дату.
        if work_date > date.today():
            raise TimesheetFactFutureDateError(
                "Cannot enter actual hours for a future date"
            )

        # Проверяем, существует ли план на эту дату.
        plans = self._timesheet_plan_repository.get_by_employee_id(employee_id)

        planned_hours = None

        for plan in plans:
            if plan.work_date == work_date:
                planned_hours = plan.planned_hours
                break

        if planned_hours is None:
            raise ValueError(
                "Timesheet plan not found for employee and date"
            )

        # Факт должен соответствовать плану.
        if actual_hours != planned_hours:
            raise TimesheetFactHoursMismatchError(
                f"Actual hours must equal planned hours: {planned_hours}"
            )

        # Проверяем, нет ли уже факта.
        existing_facts = (
            self._timesheet_fact_repository.get_by_employee_id(employee_id)
        )

        for fact in existing_facts:
            if fact.work_date == work_date:
                raise TimesheetFactAlreadyExistsError(
                    "Timesheet fact already exists for employee and date"
                )

        timesheet_fact = TimesheetFact(
            employee_id=employee_id,
            work_date=work_date,
            actual_hours=actual_hours,
        )

        return self._timesheet_fact_repository.create(timesheet_fact)

    def get_by_id(self, timesheet_fact_id: int) -> TimesheetFact:
        timesheet_fact = self._timesheet_fact_repository.get_by_id(
            timesheet_fact_id
        )

        if timesheet_fact is None:
            raise TimesheetFactNotFoundError(
                f"Timesheet fact with id {timesheet_fact_id} not found"
            )

        return timesheet_fact

    def get_all(self) -> list[TimesheetFact]:
        return self._timesheet_fact_repository.get_all()

    def get_by_employee_id(
        self,
        employee_id: int,
    ) -> list[TimesheetFact]:
        return self._timesheet_fact_repository.get_by_employee_id(
            employee_id
        )

    def update(
        self,
        timesheet_fact_id: int,
        actual_hours: float,
    ) -> TimesheetFact:
        timesheet_fact = self.get_by_id(timesheet_fact_id)

        # Нельзя менять факт на будущую дату.
        if timesheet_fact.work_date > date.today():
            raise TimesheetFactFutureDateError(
                "Cannot update actual hours for a future date"
            )

        # Находим план.
        plans = self._timesheet_plan_repository.get_by_employee_id(
            timesheet_fact.employee_id
        )

        planned_hours = None

        for plan in plans:
            if plan.work_date == timesheet_fact.work_date:
                planned_hours = plan.planned_hours
                break

        if planned_hours is None:
            raise ValueError(
                "Timesheet plan not found for employee and date"
            )

        # Проверяем соответствие факта плану.
        if actual_hours != planned_hours:
            raise TimesheetFactHoursMismatchError(
                f"Actual hours must equal planned hours: {planned_hours}"
            )

        timesheet_fact.actual_hours = actual_hours

        return self._timesheet_fact_repository.update(timesheet_fact)

    def delete(self, timesheet_fact_id: int) -> None:
        timesheet_fact = self.get_by_id(timesheet_fact_id)

        self._timesheet_fact_repository.delete(timesheet_fact)