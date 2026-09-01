from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controllers.employee import router as employee_router
from app.controllers.organization import router as organization_router
from app.controllers.timesheet import router as timesheet_router

from app.services.employee import EmployeeNotFoundError
from app.services.organization import OrganizationNotFoundError
from app.services.timesheet import (
    TimesheetPlanAlreadyExistsError,
    TimesheetPlanNotFoundError,
)


app = FastAPI()

app.include_router(organization_router)
app.include_router(employee_router)
app.include_router(timesheet_router)


@app.exception_handler(OrganizationNotFoundError)
async def handle_organization_not_found(
    request: Request,
    exc: OrganizationNotFoundError,
) -> JSONResponse:

    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(EmployeeNotFoundError)
async def handle_employee_not_found(
    request: Request,
    exc: EmployeeNotFoundError,
) -> JSONResponse:

    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(TimesheetPlanNotFoundError)
async def handle_timesheet_plan_not_found(
    request: Request,
    exc: TimesheetPlanNotFoundError,
) -> JSONResponse:

    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(TimesheetPlanAlreadyExistsError)
async def handle_timesheet_plan_already_exists(
    request: Request,
    exc: TimesheetPlanAlreadyExistsError,
) -> JSONResponse:

    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )


@app.get("/")
def read_root():
    return {
        "message": "Timesheet API работает!"
    }


@app.get("/hello")
def hello():
    return {
        "message": "Привет!"
    }