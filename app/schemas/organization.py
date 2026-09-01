from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    name: str = Field(max_length=200)
    full_name: str = Field(max_length=500)
    inn: str = Field(max_length=12)
    taxation_system: str = Field(max_length=100)
    director: str = Field(max_length=200)
    chief_accountant: str = Field(max_length=200)
    is_active: bool = True


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    full_name: str | None = Field(default=None, max_length=500)
    inn: str | None = Field(default=None, max_length=12)
    taxation_system: str | None = Field(default=None, max_length=100)
    director: str | None = Field(default=None, max_length=200)
    chief_accountant: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    full_name: str
    inn: str
    taxation_system: str
    director: str
    chief_accountant: str
    is_active: bool
