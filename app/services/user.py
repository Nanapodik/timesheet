from app.models.user import User
from app.repositories.user import UserRepository
from app.security import hash_password, verify_password


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    def register(
        self,
        username: str,
        password: str,
    ) -> User:
        existing_user = self.user_repository.get_by_username(
            username
        )

        if existing_user is not None:
            raise UserAlreadyExistsError(
                f"User with username '{username}' already exists"
            )

        password_hash = hash_password(password)

        return self.user_repository.create(
            username=username,
            password_hash=password_hash,
        )

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> User:
        user = self.user_repository.get_by_username(
            username
        )

        if user is None:
            raise InvalidCredentialsError(
                "Invalid username or password"
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsError(
                "Invalid username or password"
            )

        if not user.is_active:
            raise InvalidCredentialsError(
                "User is inactive"
            )

        return user

    def get_by_id(
        self,
        user_id: int,
    ) -> User:
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError(
                f"User with id={user_id} not found"
            )

        return user

    def get_all(self) -> list[User]:
        return self.user_repository.get_all()

    def delete(
        self,
        user_id: int,
    ) -> None:
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError(
                f"User with id={user_id} not found"
            )

        self.user_repository.delete(user)