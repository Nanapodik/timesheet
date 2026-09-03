from calendar import monthrange
from datetime import date

from app.repositories.timesheet import TimesheetPlanRepository
from app.repositories.timesheet_fact import TimesheetFactRepository
from app.schemas.timesheet_report import (
    TimesheetReportDay,
    TimesheetReportResponse,
)
from app.services.employee import (
    EmployeeNotFoundError,
    EmployeeService,
)


class TimesheetReportService:

    def __init__(
        self,
        timesheet_plan_repository: TimesheetPlanRepository,
        timesheet_fact_repository: TimesheetFactRepository,
        employee_service: EmployeeService,
    ) -> None:

        self._timesheet_plan_repository = (
            timesheet_plan_repository
        )

        self._timesheet_fact_repository = (
            timesheet_fact_repository
        )

        self._employee_service = employee_service

    def get_month_report(
        self,
        employee_id: int,
        year: int,
        month: int,
    ) -> TimesheetReportResponse:

        # Проверяем существование сотрудника.
        employee = self._employee_service.get_by_id(
            employee_id
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        # Проверяем корректность месяца.
        if month < 1 or month > 12:
            raise ValueError(
                "Month must be between 1 and 12"
            )

        # Определяем первый день месяца.
        first_day = date(
            year,
            month,
            1,
        )

        # Определяем последний день месяца.
        last_day = date(
            year,
            month,
            monthrange(
                year,
                month,
            )[1],
        )

        # Получаем планы сотрудника за месяц.
        plans = (
            self._timesheet_plan_repository
            .get_by_employee_and_date_range(
                employee_id=employee_id,
                start_date=first_day,
                end_date=last_day,
            )
        )

        # Получаем факты сотрудника за месяц.
        facts = (
            self._timesheet_fact_repository
            .get_by_employee_and_date_range(
                employee_id=employee_id,
                start_date=first_day,
                end_date=last_day,
            )
        )

        # Создаём словарь фактов:
        # дата -> количество фактических часов.
        facts_by_date = {
            fact.work_date: fact.actual_hours
            for fact in facts
        }

        days: list[TimesheetReportDay] = []

        planned_total = 0.0
        actual_total = 0.0

        # Формируем строки отчёта.
        for plan in plans:

            actual_hours = facts_by_date.get(
                plan.work_date
            )

            days.append(
                TimesheetReportDay(
                    work_date=plan.work_date,
                    planned_hours=plan.planned_hours,
                    actual_hours=actual_hours,
                )
            )

            planned_total += plan.planned_hours

            if actual_hours is not None:
                actual_total += actual_hours

        difference = actual_total - planned_total

        return TimesheetReportResponse(
            employee_id=employee_id,
            year=year,
            month=month,
            planned_total=planned_total,
            actual_total=actual_total,
            difference=difference,
            days=days,
        )