from unittest.mock import Mock

import pytest

from app.models.user import User
from app.services.user import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)


def test_register_user_success():
    repository = Mock()

    repository.get_by_username.return_value = None

    created_user = User(
        id=1,
        username="andrei",
        password_hash="$2b$12$example",
        is_active=True,
    )

    repository.create.return_value = created_user

    service = UserService(repository)

    result = service.register(
        username="andrei",
        password="TestPassword123",
    )

    assert result == created_user

    repository.get_by_username.assert_called_once_with(
        "andrei"
    )

    repository.create.assert_called_once()

    created_username = (
        repository.create.call_args.kwargs["username"]
    )

    created_password_hash = (
        repository.create.call_args.kwargs["password_hash"]
    )

    assert created_username == "andrei"

    assert created_password_hash != "TestPassword123"

    assert created_password_hash.startswith("$2b$")


def test_register_user_already_exists():
    repository = Mock()

    existing_user = User(
        id=1,
        username="andrei",
        password_hash="$2b$12$example",
        is_active=True,
    )

    repository.get_by_username.return_value = existing_user

    service = UserService(repository)

    with pytest.raises(UserAlreadyExistsError):
        service.register(
            username="andrei",
            password="TestPassword123",
        )

    repository.get_by_username.assert_called_once_with(
        "andrei"
    )

    repository.create.assert_not_called()


def test_authenticate_success():
    repository = Mock()

    password_hash = (
        "$2b$12$zBRMHojNI31PGlFQWEDsZOAKgowvVTtAyq."
        "vgsMsxmQ.kybMfSpJi"
    )

    user = User(
        id=1,
        username="andrei",
        password_hash=password_hash,
        is_active=True,
    )

    repository.get_by_username.return_value = user

    service = UserService(repository)

    result = service.authenticate(
        username="andrei",
        password="TestPassword123",
    )

    assert result == user

    repository.get_by_username.assert_called_once_with(
        "andrei"
    )


def test_authenticate_wrong_password():
    repository = Mock()

    password_hash = (
        "$2b$12$zBRMHojNI31PGlFQWEDsZOAKgowvVTtAyq."
        "vgsMsxmQ.kybMfSpJi"
    )

    user = User(
        id=1,
        username="andrei",
        password_hash=password_hash,
        is_active=True,
    )

    repository.get_by_username.return_value = user

    service = UserService(repository)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(
            username="andrei",
            password="WrongPassword",
        )


def test_authenticate_user_not_found():
    repository = Mock()

    repository.get_by_username.return_value = None

    service = UserService(repository)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(
            username="unknown",
            password="TestPassword123",
        )

    repository.get_by_username.assert_called_once_with(
        "unknown"
    )


def test_authenticate_inactive_user():
    repository = Mock()

    password_hash = (
        "$2b$12$zBRMHojNI31PGlFQWEDsZOAKgowvVTtAyq."
        "vgsMsxmQ.kybMfSpJi"
    )

    user = User(
        id=1,
        username="andrei",
        password_hash=password_hash,
        is_active=False,
    )

    repository.get_by_username.return_value = user

    service = UserService(repository)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(
            username="andrei",
            password="TestPassword123",
        )


def test_get_user_success():
    repository = Mock()

    user = User(
        id=1,
        username="andrei",
        password_hash="$2b$12$example",
        is_active=True,
    )

    repository.get_by_id.return_value = user

    service = UserService(repository)

    result = service.get_by_id(1)

    assert result == user

    repository.get_by_id.assert_called_once_with(1)


def test_get_user_not_found():
    repository = Mock()

    repository.get_by_id.return_value = None

    service = UserService(repository)

    with pytest.raises(UserNotFoundError):
        service.get_by_id(999)

    repository.get_by_id.assert_called_once_with(999)