from typing import List, Optional, Set

from fastapi import APIRouter, Depends, Path, Query, Request, Response
from pydantic import Json
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.dependencies import repository_manager
from app.filters.author import AuthorFilter, AuthorOrderBy
from app.filters.manager import HasManagerFilter, ManagerFilter, ManagerOrderBy
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.internal.response import PaginatedData
from app.models.author import Author, AuthorInBase, AuthorOutWithoutRelations
from app.models.manager import ManagerIn, ManagerOut, ManagerPatchBody

router = APIRouter(prefix="/api/managers", tags=["managers-controller"])


@router.get(
    "",
    name="managers:list",
    response_model=PaginatedData[ManagerOut],
    summary="Query all Manager records",
)
async def list_all(
    request: Request,
    response: Response,
    where: Optional[Json] = Query(None),
    order_by: ManagerOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    total = repository.manager.find_all(
        pagination, ManagerFilter.from_query(request), order_by, True
    )
    items = repository.manager.find_all(
        pagination, ManagerFilter.from_query(request), order_by
    )
    return PaginatedData(
        items=[ManagerOut.from_orm(item) for item in items], total=total
    )


@router.get(
    "/{id}", name="managers:get", response_model=ManagerOut, summary="Get Manager by id"
)
async def get_by_id(
    id: int = Path(...),
    exclude: Set[str] = Query({}),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.manager.find_by_id(id)


@router.post(
    "",
    name="managers:create",
    response_model=ManagerOut,
    status_code=HTTP_201_CREATED,
    summary="Create new Manager",
)
async def create_new(
    manager_in: ManagerIn,
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.manager.create(manager_in)


@router.put(
    "/{id}",
    name="managers:update",
    response_model=ManagerOut,
    summary="Update Manager by id",
)
async def update(
    manager_in: ManagerIn,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.manager.update(id, manager_in)


@router.patch(
    "/{id}",
    name="managers:patch",
    response_model=ManagerOut,
    summary="Partial Update Manager by id",
)
async def patch_update(
    manager_in: ManagerPatchBody,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.manager.patch(id, manager_in)


@router.delete(
    "",
    name="managers:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete Manager by id",
)
async def delete_manager(
    request: Request,
    where: Optional[Json] = Query(None),
    repository: RepositoryManager = Depends(repository_manager),
):
    repository.manager.delete(ManagerFilter.from_query(request))
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/authors",
    name="managers:authors:get",
    response_model=PaginatedData[AuthorOutWithoutRelations],
    summary="Get linked authors(Author)",
)
async def get_authors(
    request: Request,
    id: int = Path(...),
    where: Optional[Json] = Query(None),
    order_by: AuthorOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    where = AuthorFilter.from_query(request)
    if where is None:
        where = AuthorFilter()
    where.manager = HasManagerFilter(id=id)
    total = repository.author.find_all(pagination, where, order_by, count=True)
    items = repository.author.find_all(pagination, where, order_by)
    return PaginatedData(
        items=[AuthorOutWithoutRelations.from_orm(item) for item in items], total=total
    )


@router.post(
    "/{id}/authors",
    name="managers:authors:add",
    response_model=AuthorOutWithoutRelations,
    status_code=HTTP_201_CREATED,
    summary="Add authors(Author)",
)
async def add_authors(
    author_in: AuthorInBase,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    manager = repository.manager.find_by_id(id)
    new_author = Author(**author_in.dict())
    manager.authors.append(new_author)
    return repository.save(new_author)


@router.put(
    "/{id}/authors",
    name="managers:authors:put",
    response_model=List[AuthorOutWithoutRelations],
    summary="Set authors(Author) by ids",
)
async def set_existing_authors(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    manager = repository.manager.find_by_id(id)
    manager.authors = repository.author.find_by_ids(ids)
    repository.save(manager)
    return repository.author.find_by_ids(ids)
