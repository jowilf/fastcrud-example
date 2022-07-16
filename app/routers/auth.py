from fastapi import APIRouter, Depends
from starlette.status import HTTP_201_CREATED

from app.dependencies import repository_manager
from app.internal.repository_manager import RepositoryManager
from app.models.auth import LoginBody, TokenResponse
from app.models.user import UserOut, UserRegister
from app.services.auth import authorize

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get(
    "/me",
    response_model=UserOut,
    status_code=HTTP_201_CREATED,
    summary="Get connected User info",
)
async def me(user=Depends(authorize())):
    return user


@router.post(
    "/register",
    response_model=UserOut,
    status_code=HTTP_201_CREATED,
    summary="Register new User",
)
async def register_new_user(
    user_in: UserRegister, repository: RepositoryManager = Depends(repository_manager)
):
    return repository.user.create(user_in)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginBody, repository: RepositoryManager = Depends(repository_manager)
):
    return repository.user.login(body)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str, repository: RepositoryManager = Depends(repository_manager)
):
    return repository.user.refresh_token(refresh_token)
