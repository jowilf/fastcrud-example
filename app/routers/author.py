from typing import List, Optional, Set

from fastapi import (APIRouter, Depends, HTTPException, Path, Query, Request,
                     Response)
from pydantic import Json
from starlette.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                              HTTP_404_NOT_FOUND)

from app.dependencies import repository_manager
from app.filters.author import AnyAuthorFilter, AuthorFilter, AuthorOrderBy
from app.filters.movie import MovieFilter, MovieOrderBy
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.internal.response import PaginatedData
from app.models.author import (Author, AuthorIn, AuthorInBase, AuthorOut,
                               AuthorOutWithoutRelations, AuthorPatchBody)
from app.models.author_profile import AuthorProfileOutWithoutRelations
from app.models.manager import ManagerOutWithoutRelations
from app.models.movie import Movie, MovieInBase, MovieOutWithoutRelations
from app.models.user import User
from app.services.auth import authorize

router = APIRouter(prefix="/api/authors", tags=["authors-controller"])


@router.get(
    "",
    name="authors:list",
    response_model=PaginatedData[AuthorOut],
    summary="Query all Author records",
)
async def list_all(
    request: Request,
    response: Response,
    where: Optional[Json] = Query(None),
    order_by: AuthorOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    total = repository.author.find_all(
        pagination, AuthorFilter.from_query(request), order_by, True
    )
    items = repository.author.find_all(
        pagination, AuthorFilter.from_query(request), order_by
    )
    return PaginatedData(
        items=[AuthorOut.from_orm(item) for item in items], total=total
    )


@router.get(
    "/{id}", name="authors:get", response_model=AuthorOut, summary="Get Author by id"
)
async def get_by_id(
    id: int = Path(...),
    exclude: Set[str] = Query({}),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.author.find_by_id(id)


@router.post(
    "",
    name="authors:create",
    response_model=AuthorOut,
    status_code=HTTP_201_CREATED,
    summary="Create new Author",
)
async def create_new(
    author_in: AuthorIn,
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.author.create(author_in)


@router.put(
    "/{id}",
    name="authors:update",
    response_model=AuthorOut,
    summary="Update Author by id",
)
async def update(
    author_in: AuthorIn,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.author.update(id, author_in)


@router.patch(
    "/{id}",
    name="authors:patch",
    response_model=AuthorOut,
    summary="Partial Update Author by id",
)
async def patch_update(
    author_in: AuthorPatchBody,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.author.patch(id, author_in)


@router.delete(
    "",
    name="authors:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete Author by id",
)
async def delete_author(
    request: Request,
    where: Optional[Json] = Query(None),
    repository: RepositoryManager = Depends(repository_manager),
):
    repository.author.delete(AuthorFilter.from_query(request))
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/manager",
    name="authors:manager:get",
    response_model=ManagerOutWithoutRelations,
    summary="Get linked manager(Manager)",
)
async def get_manager(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    if author.manager is None:
        raise HTTPException(HTTP_404_NOT_FOUND)
    return author.manager


@router.put(
    "/{id}/manager/{manager_id}",
    name="authors:manager:put",
    response_model=ManagerOutWithoutRelations,
    summary="Linked with manager(Manager) by id",
)
async def link_manager(
    id: int = Path(...),
    manager_id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.manager_id = repository.manager.find_by_id(manager_id).id
    return repository.save(author).manager


@router.delete(
    "/{id}/manager",
    name="authors:manager:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete linked manager(Manager)",
)
async def delete_manager(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.manager = None
    repository.save(author)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/profile",
    name="authors:profile:get",
    response_model=AuthorProfileOutWithoutRelations,
    summary="Get linked profile(AuthorProfile)",
)
async def get_profile(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    if author.profile is None:
        raise HTTPException(HTTP_404_NOT_FOUND)
    return author.profile


@router.put(
    "/{id}/profile/{profile_id}",
    name="authors:profile:put",
    response_model=AuthorProfileOutWithoutRelations,
    summary="Linked with profile(AuthorProfile) by id",
)
async def link_profile(
    id: int = Path(...),
    profile_id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    profile = repository.author_profile.find_by_id(profile_id)
    if profile.author is not None:
        profile.author = None
        repository.save(profile)
    author.profile_id = profile.id
    return repository.save(author).profile


@router.delete(
    "/{id}/profile",
    name="authors:profile:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete linked profile(AuthorProfile)",
)
async def delete_profile(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.profile = None
    repository.save(author)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/movies",
    name="authors:movies:get",
    response_model=PaginatedData[MovieOutWithoutRelations],
    summary="Get linked movies(Movie)",
)
async def get_movies(
    request: Request,
    id: int = Path(...),
    where: Optional[Json] = Query(None),
    order_by: MovieOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie:view"])),
):
    where = MovieFilter.from_query(request)
    if where is None:
        where = MovieFilter()
    where.authors = AnyAuthorFilter(id=id)
    total = repository.movie.find_all(pagination, where, order_by, count=True)
    items = repository.movie.find_all(pagination, where, order_by)
    return PaginatedData(
        items=[MovieOutWithoutRelations.from_orm(item) for item in items], total=total
    )


@router.post(
    "/{id}/movies",
    name="authors:movies:add",
    response_model=MovieOutWithoutRelations,
    status_code=HTTP_201_CREATED,
    summary="Add movies(Movie)",
)
async def add_movies(
    movie_in: MovieInBase,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie:create"])),
):
    author = repository.author.find_by_id(id)
    new_movie = Movie(**movie_in.dict())
    author.movies.append(new_movie)
    return repository.save(new_movie)


@router.put(
    "/{id}/movies",
    name="authors:movies:put",
    response_model=List[MovieOutWithoutRelations],
    summary="Set movies(Movie) by ids",
)
async def set_existing_movies(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.movies = repository.movie.find_by_ids(ids)
    repository.save(author)
    return repository.movie.find_by_ids(ids)


@router.patch(
    "/{id}/movies",
    name="authors:movies:patch",
    response_model=List[MovieOutWithoutRelations],
    summary="Add movies(Movie) by ids",
)
async def add_existing_movies(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.movies.extend(repository.movie.find_by_ids(ids))
    repository.save(author)
    return repository.movie.find_by_ids(ids)


@router.get(
    "/{id}/friends",
    name="authors:friends:get",
    response_model=PaginatedData[AuthorOutWithoutRelations],
    summary="Get linked friends(Author)",
)
async def get_friends(
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
    where.friends_of = AnyAuthorFilter(id=id)
    total = repository.author.find_all(pagination, where, order_by, count=True)
    items = repository.author.find_all(pagination, where, order_by)
    return PaginatedData(
        items=[AuthorOutWithoutRelations.from_orm(item) for item in items], total=total
    )


@router.post(
    "/{id}/friends",
    name="authors:friends:add",
    response_model=AuthorOutWithoutRelations,
    status_code=HTTP_201_CREATED,
    summary="Add friends(Author)",
)
async def add_friends(
    author_in: AuthorInBase,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    new_author = Author(**author_in.dict())
    author.friends.append(new_author)
    return repository.save(new_author)


@router.put(
    "/{id}/friends",
    name="authors:friends:put",
    response_model=List[AuthorOutWithoutRelations],
    summary="Set friends(Author) by ids",
)
async def set_existing_friends(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.friends = repository.author.find_by_ids(ids)
    repository.save(author)
    return repository.author.find_by_ids(ids)


@router.patch(
    "/{id}/friends",
    name="authors:friends:patch",
    response_model=List[AuthorOutWithoutRelations],
    summary="Add friends(Author) by ids",
)
async def add_existing_friends(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.friends.extend(repository.author.find_by_ids(ids))
    repository.save(author)
    return repository.author.find_by_ids(ids)


@router.get(
    "/{id}/friends_of",
    name="authors:friends_of:get",
    response_model=PaginatedData[AuthorOutWithoutRelations],
    summary="Get linked friends_of(Author)",
)
async def get_friends_of(
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
    where.friends = AnyAuthorFilter(id=id)
    total = repository.author.find_all(pagination, where, order_by, count=True)
    items = repository.author.find_all(pagination, where, order_by)
    return PaginatedData(
        items=[AuthorOutWithoutRelations.from_orm(item) for item in items], total=total
    )


@router.post(
    "/{id}/friends_of",
    name="authors:friends_of:add",
    response_model=AuthorOutWithoutRelations,
    status_code=HTTP_201_CREATED,
    summary="Add friends_of(Author)",
)
async def add_friends_of(
    author_in: AuthorInBase,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    new_author = Author(**author_in.dict())
    author.friends_of.append(new_author)
    return repository.save(new_author)


@router.put(
    "/{id}/friends_of",
    name="authors:friends_of:put",
    response_model=List[AuthorOutWithoutRelations],
    summary="Set friends_of(Author) by ids",
)
async def set_existing_friends_of(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.friends_of = repository.author.find_by_ids(ids)
    repository.save(author)
    return repository.author.find_by_ids(ids)


@router.patch(
    "/{id}/friends_of",
    name="authors:friends_of:patch",
    response_model=List[AuthorOutWithoutRelations],
    summary="Add friends_of(Author) by ids",
)
async def add_existing_friends_of(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author = repository.author.find_by_id(id)
    author.friends_of.extend(repository.author.find_by_ids(ids))
    repository.save(author)
    return repository.author.find_by_ids(ids)
