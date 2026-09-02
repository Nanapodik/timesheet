from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        username: str,
        password_hash: str,
    ) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        statement = select(User).where(
            User.id == user_id
        )

        return self.session.scalar(statement)

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        statement = select(User).where(
            User.username == username
        )

        return self.session.scalar(statement)

    def get_all(self) -> list[User]:
        statement = select(User).order_by(User.id)

        return list(
            self.session.scalars(statement)
        )

    def delete(
        self,
        user: User,
    ) -> None:
        self.session.delete(user)
        self.session.commit()