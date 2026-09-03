from datetime import date

from fastapi.testclient import TestClient

from app.database.connection import SessionLocal, engine
from app.main import app
from app.models.employee import Employee
from app.models.organization import Organization
from app.models.timesheet import TimesheetPlan
from app.models.timesheet_fact import TimesheetFact
from app.models.user import User
from app.security import hash_password


def clear_test_database() -> None:
    """
    Очищает только рабочие таблицы тестовой базы.

    Таблица alembic_version не затрагивается.
    """
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            TRUNCATE TABLE
                timesheet_facts,
                timesheet_plans,
                employees,
                organizations,
                users
            RESTART IDENTITY CASCADE
            """
        )


def create_test_admin() -> None:
    """
    Создаёт администратора непосредственно в тестовой БД.

    Это техническая подготовка теста:
    API не предоставляет возможность обычному пользователю
    самостоятельно назначить себе роль admin.
    """
    session = SessionLocal()

    try:
        admin = User(
            username="integration_admin",
            password_hash=hash_password("IntegrationPassword123"),
            is_active=True,
            role="admin",
        )

        session.add(admin)
        session.commit()

    finally:
        session.close()


def test_full_timesheet_integration_scenario():
    """
    Полный интеграционный сценарий:

    1. Подготавливаем тестовую БД.
    2. Создаём admin.
    3. Выполняем login.
    4. Получаем JWT.
    5. Создаём организацию.
    6. Создаём сотрудника.
    7. Создаём план рабочего времени.
    8. Фиксируем месяц.
    9. Вносим фактические часы.
    10. Получаем месячный отчёт.
    11. Проверяем итоговые значения.
    """

    clear_test_database()
    create_test_admin()

    client = TestClient(app)

    # ============================================================
    # 1. LOGIN
    # ============================================================

    login_response = client.post(
        "/auth/login",
        json={
            "username": "integration_admin",
            "password": "IntegrationPassword123",
        },
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    access_token = login_data["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # ============================================================
    # 2. GET CURRENT USER
    # ============================================================

    me_response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert me_response.status_code == 200

    me_data = me_response.json()

    assert me_data["username"] == "integration_admin"
    assert me_data["is_active"] is True

    # ============================================================
    # 3. CREATE ORGANIZATION
    # ============================================================

    organization_response = client.post(
        "/organizations",
        headers=headers,
        json={
            "name": "Тестовая организация",
            "full_name": (
                "Общество с ограниченной ответственностью "
                "\"Тестовая организация\""
            ),
            "inn": "123456789012",
            "taxation_system": "УСН",
            "director": "Иванов Иван Иванович",
            "chief_accountant": "Петрова Анна Сергеевна",
            "is_active": True,
        },
    )

    assert organization_response.status_code == 201

    organization_data = organization_response.json()

    assert organization_data["name"] == "Тестовая организация"
    assert organization_data["inn"] == "123456789012"

    organization_id = organization_data["id"]

    # ============================================================
    # 4. CREATE EMPLOYEE
    # ============================================================

    employee_response = client.post(
        "/employees",
        headers=headers,
        json={
            "first_name": "Алексей",
            "last_name": "Смирнов",
            "middle_name": "Петрович",
            "birth_date": "1995-05-15",
            "organization_id": organization_id,
            "is_active": True,
        },
    )

    assert employee_response.status_code == 201

    employee_data = employee_response.json()

    assert employee_data["first_name"] == "Алексей"
    assert employee_data["last_name"] == "Смирнов"
    assert employee_data["organization_id"] == organization_id

    employee_id = employee_data["id"]

    # ============================================================
    # 5. CREATE TIMESHEET PLAN
    # ============================================================

    work_date = date(2026, 9, 2)

    plan_response = client.post(
        "/timesheet-plans",
        headers=headers,
        json={
            "employee_id": employee_id,
            "work_date": work_date.isoformat(),
            "planned_hours": 8,
        },
    )

    assert plan_response.status_code == 201

    plan_data = plan_response.json()

    assert plan_data["employee_id"] == employee_id
    assert plan_data["work_date"] == work_date.isoformat()
    assert plan_data["planned_hours"] == 8
    assert plan_data["is_fixed"] is False

    # ============================================================
    # 6. FIX SEPTEMBER 2026
    # ============================================================

    fix_response = client.post(
        f"/timesheet-plans/employee/{employee_id}/month/2026/9/fix",
        headers=headers,
    )

    assert fix_response.status_code == 200

    fixed_plans = fix_response.json()

    assert len(fixed_plans) == 1

    assert fixed_plans[0]["employee_id"] == employee_id
    assert fixed_plans[0]["work_date"] == work_date.isoformat()
    assert fixed_plans[0]["planned_hours"] == 8
    assert fixed_plans[0]["is_fixed"] is True

    # ============================================================
    # 7. CREATE ACTUAL FACT
    # ============================================================

    fact_response = client.post(
        "/timesheet-facts",
        headers=headers,
        json={
            "employee_id": employee_id,
            "work_date": work_date.isoformat(),
            "actual_hours": 8,
        },
    )

    assert fact_response.status_code == 201

    fact_data = fact_response.json()

    assert fact_data["employee_id"] == employee_id
    assert fact_data["work_date"] == work_date.isoformat()
    assert fact_data["actual_hours"] == 8

    # ============================================================
    # 8. GET MONTHLY REPORT
    # ============================================================

    report_response = client.get(
        f"/timesheet-reports/employee/{employee_id}/month/2026/9",
        headers=headers,
    )

    assert report_response.status_code == 200

    report_data = report_response.json()

    # Проверяем общую информацию
    assert report_data["employee_id"] == employee_id
    assert report_data["year"] == 2026
    assert report_data["month"] == 9

    # Проверяем итоги
    assert report_data["planned_total"] == 8
    assert report_data["actual_total"] == 8
    assert report_data["difference"] == 0

    # Проверяем конкретный день
    assert len(report_data["days"]) == 1

    day_data = report_data["days"][0]

    assert day_data["work_date"] == work_date.isoformat()
    assert day_data["planned_hours"] == 8
    assert day_data["actual_hours"] == 8

    # ============================================================
    # 9. FINAL DATABASE CHECK
    # ============================================================

    session = SessionLocal()

    try:
        organization = session.get(
            Organization,
            organization_id,
        )

        employee = session.get(
            Employee,
            employee_id,
        )

        plan = session.get(
            TimesheetPlan,
            plan_data["id"],
        )

        fact = session.get(
            TimesheetFact,
            fact_data["id"],
        )

        assert organization is not None
        assert employee is not None
        assert plan is not None
        assert fact is not None

        assert employee.organization_id == organization.id
        assert plan.employee_id == employee.id
        assert fact.employee_id == employee.id

        assert plan.planned_hours == 8
        assert fact.actual_hours == 8

    finally:
        session.close()