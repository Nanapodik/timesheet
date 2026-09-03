from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, get_user_service
from app.schemas.user import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.security import create_access_token
from app.services.user import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserService,
)
from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserRegister,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        user = service.register(
            username=data.username,
            password=data.password,
        )
    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: UserLogin,
    service: UserService = Depends(get_user_service),
) -> TokenResponse:
    try:
        user = service.authenticate(
            username=data.username,
            password=data.password,
        )
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)