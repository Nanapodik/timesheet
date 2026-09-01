from app.models.organization import Organization
from app.repositories.organization import OrganizationRepository


class OrganizationNotFoundError(Exception):
    def __init__(self, organization_id: int) -> None:
        self.organization_id = organization_id
        super().__init__(f"Organization with id={organization_id} not found")


class OrganizationService:
    def __init__(self, repository: OrganizationRepository) -> None:
        self._repository = repository

    def create(
        self,
        name: str,
        full_name: str,
        inn: str,
        taxation_system: str,
        director: str,
        chief_accountant: str,
        is_active: bool = True,
    ) -> Organization:
        organization = Organization(
            name=name,
            full_name=full_name,
            inn=inn,
            taxation_system=taxation_system,
            director=director,
            chief_accountant=chief_accountant,
            is_active=is_active,
        )
        return self._repository.create(organization)

    def get_by_id(self, organization_id: int) -> Organization | None:
        return self._repository.get_by_id(organization_id)

    def get_all(self) -> list[Organization]:
        return self._repository.get_all()

    def update(
        self,
        organization_id: int,
        name: str | None = None,
        full_name: str | None = None,
        inn: str | None = None,
        taxation_system: str | None = None,
        director: str | None = None,
        chief_accountant: str | None = None,
        is_active: bool | None = None,
    ) -> Organization:
        organization = self._get_existing(organization_id)

        if name is not None:
            organization.name = name
        if full_name is not None:
            organization.full_name = full_name
        if inn is not None:
            organization.inn = inn
        if taxation_system is not None:
            organization.taxation_system = taxation_system
        if director is not None:
            organization.director = director
        if chief_accountant is not None:
            organization.chief_accountant = chief_accountant
        if is_active is not None:
            organization.is_active = is_active

        return self._repository.update(organization)

    def delete(self, organization_id: int) -> None:
        organization = self._get_existing(organization_id)
        self._repository.delete(organization)

    def _get_existing(self, organization_id: int) -> Organization:
        organization = self._repository.get_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(organization_id)
        return organization
