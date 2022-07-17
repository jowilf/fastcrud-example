from typing import Optional, Set

from fastapi import APIRouter, Depends, Path, Query, Request, Response
from pydantic import Json
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.dependencies import repository_manager
from app.filters.user import UserFilter, UserOrderBy
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.internal.response import PaginatedData
from app.models.user import UserIn, UserOut, UserPatchBody, UserRegister

router = APIRouter(prefix="/api/users", tags=["users-controller"])


@router.get(
    "",
    name="users:list",
    response_model=PaginatedData[UserOut],
    summary="Query all User records",
)
async def list_all(
    request: Request,
    response: Response,
    where: Optional[Json] = Query(None),
    order_by: UserOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    total = repository.user.find_all(
        pagination, UserFilter.from_query(request), order_by, True
    )
    items = repository.user.find_all(
        pagination, UserFilter.from_query(request), order_by
    )
    return PaginatedData(items=[UserOut.from_orm(item) for item in items], total=total)


@router.get("/{id}", name="users:get", response_model=UserOut, summary="Get User by id")
async def get_by_id(
    id: int = Path(...),
    exclude: Set[str] = Query({}),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.user.find_by_id(id)


@router.post(
    "",
    name="users:create",
    response_model=UserOut,
    status_code=HTTP_201_CREATED,
    summary="Create new User",
)
async def create_new_user(
    user_in: UserRegister,
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.user.create(user_in)


@router.put(
    "/{id}", name="users:update", response_model=UserOut, summary="Update User by id"
)
async def update(
    user_in: UserIn,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.user.update(id, user_in)


@router.patch(
    "/{id}",
    name="users:patch",
    response_model=UserOut,
    summary="Partial Update User by id",
)
async def patch_update(
    user_in: UserPatchBody,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.user.patch(id, user_in)


@router.delete(
    "",
    name="users:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete User by id",
)
async def delete_user(
    request: Request,
    where: Optional[Json] = Query(None),
    repository: RepositoryManager = Depends(repository_manager),
):
    repository.user.delete(UserFilter.from_query(request))
    return Response(status_code=HTTP_204_NO_CONTENT)
