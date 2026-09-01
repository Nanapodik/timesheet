from fastapi import APIRouter, Depends, status

from app.dependencies import get_organization_service
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.organization import OrganizationNotFoundError, OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    payload: OrganizationCreate,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    organization = service.create(**payload.model_dump())
    return OrganizationResponse.model_validate(organization)


@router.get("", response_model=list[OrganizationResponse])
def get_organizations(
    service: OrganizationService = Depends(get_organization_service),
) -> list[OrganizationResponse]:
    organizations = service.get_all()
    return [OrganizationResponse.model_validate(item) for item in organizations]


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: int,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    organization = service.get_by_id(organization_id)
    if organization is None:
        raise OrganizationNotFoundError(organization_id)
    return OrganizationResponse.model_validate(organization)


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: int,
    payload: OrganizationUpdate,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    organization = service.update(
        organization_id,
        **payload.model_dump(exclude_unset=True),
    )
    return OrganizationResponse.model_validate(organization)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    organization_id: int,
    service: OrganizationService = Depends(get_organization_service),
) -> None:
    service.delete(organization_id)
