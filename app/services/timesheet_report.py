from calendar import monthrange
from datetime import date

from app.repositories.timesheet import TimesheetPlanRepository
from app.repositories.timesheet_fact import TimesheetFactRepository
from app.schemas.timesheet_report import (
    TimesheetReportDay,
    TimesheetReportResponse,
)


class TimesheetReportService:

    def __init__(
        self,
        timesheet_plan_repository: TimesheetPlanRepository,
        timesheet_fact_repository: TimesheetFactRepository,
    ) -> None:

        self._timesheet_plan_repository = (
            timesheet_plan_repository
        )

        self._timesheet_fact_repository = (
            timesheet_fact_repository
        )

    def get_month_report(
        self,
        employee_id: int,
        year: int,
        month: int,
    ) -> TimesheetReportResponse:

        # Определяем первый и последний день месяца.
        first_day = date(
            year,
            month,
            1,
        )

        last_day_number = monthrange(
            year,
            month,
        )[1]

        last_day = date(
            year,
            month,
            last_day_number,
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