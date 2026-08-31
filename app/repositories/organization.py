from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, organization: Organization) -> Organization:
        self._session.add(organization)
        self._session.commit()
        self._session.refresh(organization)
        return organization

    def get_by_id(self, organization_id: int) -> Organization | None:
        statement = select(Organization).where(Organization.id == organization_id)
        return self._session.scalar(statement)

    def get_all(self) -> list[Organization]:
        statement = select(Organization)
        return list(self._session.scalars(statement).all())

    def update(self, organization: Organization) -> Organization:
        self._session.commit()
        self._session.refresh(organization)
        return organization

    def delete(self, organization: Organization) -> None:
        self._session.delete(organization)
        self._session.commit()
