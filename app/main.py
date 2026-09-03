from fastapi import FastAPI, Request

from fastapi.responses import JSONResponse

from app.controllers.auth import router as auth_router
from app.controllers.employee import router as employee_router
from app.controllers.organization import router as organization_router
from app.controllers.timesheet import router as timesheet_router
from app.controllers.timesheet_fact import router as timesheet_fact_router
from app.controllers.timesheet_report import (
    router as timesheet_report_router,
)

from app.services.employee import EmployeeNotFoundError
from app.services.organization import OrganizationNotFoundError
from app.services.timesheet import (
    TimesheetPlanAlreadyExistsError,
    TimesheetPlanNotFoundError,
)


app = FastAPI()


app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(employee_router)
app.include_router(timesheet_router)
app.include_router(timesheet_fact_router)
app.include_router(timesheet_report_router)


@app.exception_handler(OrganizationNotFoundError)
async def organization_not_found_handler(
    request: Request,
    exc: OrganizationNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(EmployeeNotFoundError)
async def employee_not_found_handler(
    request: Request,
    exc: EmployeeNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(TimesheetPlanNotFoundError)
async def timesheet_plan_not_found_handler(
    request: Request,
    exc: TimesheetPlanNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(TimesheetPlanAlreadyExistsError)
async def timesheet_plan_already_exists_handler(
    request: Request,
    exc: TimesheetPlanAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


@app.get("/")
def read_root():
    return {
        "message": "Timesheet API is running"
    }


@app.get("/hello")
def hello():
    return {
        "message": "Hello!"
    }