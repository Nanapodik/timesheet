from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.timesheet_fact import TimesheetFact


class TimesheetFactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    # CREATE
    def create(
        self,
        timesheet_fact: TimesheetFact,
    ) -> TimesheetFact:

        self._session.add(timesheet_fact)
        self._session.commit()
        self._session.refresh(timesheet_fact)

        return timesheet_fact

    # GET BY ID
    def get_by_id(
        self,
        timesheet_fact_id: int,
    ) -> TimesheetFact | None:

        return self._session.get(
            TimesheetFact,
            timesheet_fact_id,
        )

    # GET ALL
    def get_all(self) -> list[TimesheetFact]:

        statement = (
            select(TimesheetFact)
            .order_by(TimesheetFact.work_date)
        )

        return list(
            self._session.scalars(statement).all()
        )

    # GET BY EMPLOYEE
    def get_by_employee_id(
        self,
        employee_id: int,
    ) -> list[TimesheetFact]:

        statement = (
            select(TimesheetFact)
            .where(
                TimesheetFact.employee_id == employee_id
            )
            .order_by(TimesheetFact.work_date)
        )

        return list(
            self._session.scalars(statement).all()
        )

    # GET BY EMPLOYEE AND DATE RANGE
    def get_by_employee_and_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
    ) -> list[TimesheetFact]:

        statement = (
            select(TimesheetFact)
            .where(
                TimesheetFact.employee_id == employee_id,
                TimesheetFact.work_date >= start_date,
                TimesheetFact.work_date <= end_date,
            )
            .order_by(TimesheetFact.work_date)
        )

        return list(
            self._session.scalars(statement).all()
        )

    # UPDATE
    def update(
        self,
        timesheet_fact: TimesheetFact,
    ) -> TimesheetFact:

        self._session.commit()
        self._session.refresh(timesheet_fact)

        return timesheet_fact

    # DELETE
    def delete(
        self,
        timesheet_fact: TimesheetFact,
    ) -> None:

        self._session.delete(timesheet_fact)
        self._session.commit()