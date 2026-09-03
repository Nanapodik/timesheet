from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.timesheet import TimesheetPlan


class TimesheetPlanRepository:

    def __init__(self, session: Session) -> None:
        self._session = session

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        timesheet_plan: TimesheetPlan,
    ) -> TimesheetPlan:

        self._session.add(timesheet_plan)
        self._session.commit()
        self._session.refresh(timesheet_plan)

        return timesheet_plan

    # ========================================================
    # GET BY ID
    # ========================================================

    def get_by_id(
        self,
        timesheet_plan_id: int,
    ) -> TimesheetPlan | None:

        return self._session.get(
            TimesheetPlan,
            timesheet_plan_id,
        )

    # ========================================================
    # GET ALL
    # ========================================================

    def get_all(self) -> list[TimesheetPlan]:

        statement = (
            select(TimesheetPlan)
            .order_by(TimesheetPlan.work_date)
        )

        return list(
            self._session.scalars(statement).all()
        )

    # ========================================================
    # GET BY EMPLOYEE
    # ========================================================

    def get_by_employee_id(
        self,
        employee_id: int,
    ) -> list[TimesheetPlan]:

        statement = (
            select(TimesheetPlan)
            .where(
                TimesheetPlan.employee_id == employee_id
            )
            .order_by(TimesheetPlan.work_date)
        )

        return list(
            self._session.scalars(statement).all()
        )

    # ========================================================
    # GET BY EMPLOYEE AND DATE
    # ========================================================

    def get_by_employee_and_date(
        self,
        employee_id: int,
        work_date: date,
    ) -> TimesheetPlan | None:

        statement = (
            select(TimesheetPlan)
            .where(
                TimesheetPlan.employee_id == employee_id,
                TimesheetPlan.work_date == work_date,
            )
        )

        return self._session.scalars(
            statement
        ).first()

    # ========================================================
    # GET BY EMPLOYEE AND DATE RANGE
    # ========================================================

    def get_by_employee_and_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
    ) -> list[TimesheetPlan]:

        statement = (
            select(TimesheetPlan)
            .where(
                TimesheetPlan.employee_id == employee_id,
                TimesheetPlan.work_date >= start_date,
                TimesheetPlan.work_date <= end_date,
            )
            .order_by(TimesheetPlan.work_date)
        )

        return list(
            self._session.scalars(statement).all()
        )

    # ========================================================
    # GET FIXED BY EMPLOYEE AND DATE RANGE
    # ========================================================

    def get_fixed_by_employee_and_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
    ) -> list[TimesheetPlan]:

        statement = (
            select(TimesheetPlan)
            .where(
                TimesheetPlan.employee_id == employee_id,
                TimesheetPlan.work_date >= start_date,
                TimesheetPlan.work_date <= end_date,
                TimesheetPlan.is_fixed.is_(True),
            )
            .order_by(TimesheetPlan.work_date)
        )

        return list(
            self._session.scalars(statement).all()
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        timesheet_plan: TimesheetPlan,
    ) -> TimesheetPlan:

        self._session.commit()
        self._session.refresh(timesheet_plan)

        return timesheet_plan

    # ========================================================
    # FIX MONTH
    # ========================================================

    def fix_month(
        self,
        plans: list[TimesheetPlan],
    ) -> list[TimesheetPlan]:

        for plan in plans:
            plan.is_fixed = True

        self._session.commit()

        for plan in plans:
            self._session.refresh(plan)

        return plans

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        timesheet_plan: TimesheetPlan,
    ) -> None:

        self._session.delete(timesheet_plan)
        self._session.commit()