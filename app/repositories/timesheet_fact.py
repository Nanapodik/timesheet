from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.timesheet_fact import TimesheetFact


class TimesheetFactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, timesheet_fact: TimesheetFact) -> TimesheetFact:
        self._session.add(timesheet_fact)
        self._session.commit()
        self._session.refresh(timesheet_fact)

        return timesheet_fact

    def get_by_id(self, timesheet_fact_id: int) -> TimesheetFact | None:
        return self._session.get(TimesheetFact, timesheet_fact_id)

    def get_all(self) -> list[TimesheetFact]:
        statement = select(TimesheetFact).order_by(TimesheetFact.work_date)

        return list(self._session.scalars(statement).all())

    def get_by_employee_id(
        self,
        employee_id: int,
    ) -> list[TimesheetFact]:
        statement = (
            select(TimesheetFact)
            .where(TimesheetFact.employee_id == employee_id)
            .order_by(TimesheetFact.work_date)
        )

        return list(self._session.scalars(statement).all())

    def update(self, timesheet_fact: TimesheetFact) -> TimesheetFact:
        self._session.commit()
        self._session.refresh(timesheet_fact)

        return timesheet_fact

    def delete(self, timesheet_fact: TimesheetFact) -> None:
        self._session.delete(timesheet_fact)
        self._session.commit()