from fastapi import FastAPI
from pydantic import BaseModel


class Employee(BaseModel):
    id: int
    first_name: str
    last_name: str
    position: str


app = FastAPI()

employees = []


@app.get("/")
def read_root():
    return {"message": "Timesheet API работает!"}


@app.get("/hello")
def hello():
    return {"message": "Привет!"}


@app.post("/employees")
def create_employee(employee: Employee):
    employees.append(employee)
    return employee


@app.get("/employees")
def get_employees():
    return employees