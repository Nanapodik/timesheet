from datetime import date

from app.database.connection import SessionLocal

# ВАЖНО:
# Импортируем связанные модели, чтобы SQLAlchemy зарегистрировал
# таблицу employees в Base.metadata.
from app.models.employee import Employee
from app.models.timesheet import TimesheetPlan
from app.models.timesheet_fact import TimesheetFact

from app.repositories.timesheet_fact import TimesheetFactRepository


session = SessionLocal()

try:
    repository = TimesheetFactRepository(session)

    # ---------------------------------------------------------
    # 1. CREATE
    # ---------------------------------------------------------

    timesheet_fact = TimesheetFact(
        employee_id=2,
        work_date=date(2026, 9, 1),
        actual_hours=8.0,
    )

    created = repository.create(timesheet_fact)

    print("Created")
    print("  id:", created.id)
    print("  employee_id:", created.employee_id)
    print("  work_date:", created.work_date)
    print("  actual_hours:", created.actual_hours)

    # ---------------------------------------------------------
    # 2. GET BY ID
    # ---------------------------------------------------------

    fetched = repository.get_by_id(created.id)

    print("Fetched by id")

    if fetched is not None:
        print("  id:", fetched.id)
        print("  actual_hours:", fetched.actual_hours)
    else:
        print("  not found")

    # ---------------------------------------------------------
    # 3. GET BY EMPLOYEE ID
    # ---------------------------------------------------------

    employee_facts = repository.get_by_employee_id(3)

    print("Fetched by employee")
    print("  count:", len(employee_facts))

    # ---------------------------------------------------------
    # 4. UPDATE
    # ---------------------------------------------------------

    created.actual_hours = 7.0

    updated = repository.update(created)

    print("Updated")
    print("  id:", updated.id)
    print("  actual_hours:", updated.actual_hours)

    # ---------------------------------------------------------
    # 5. DELETE
    # ---------------------------------------------------------

    repository.delete(updated)

    deleted = repository.get_by_id(updated.id)

    print("After delete")

    if deleted is None:
        print("  not found")
    else:
        print("  ERROR: record still exists")

finally:
    session.close()