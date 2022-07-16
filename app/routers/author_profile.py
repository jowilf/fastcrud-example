from typing import Optional, Set

from common.types import FileInfo
from fastapi import (APIRouter, Depends, File, HTTPException, Path, Query,
                     Request, Response, UploadFile)
from pydantic import Json
from starlette.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                              HTTP_404_NOT_FOUND)

from app.dependencies import repository_manager
from app.filters.author_profile import (AuthorProfileFilter,
                                        AuthorProfileOrderBy)
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.internal.response import PaginatedData
from app.models.author import AuthorOutWithoutRelations
from app.models.author_profile import (AuthorProfileIn, AuthorProfileOut,
                                       AuthorProfilePatchBody,
                                       author_profile_in_form)

router = APIRouter(prefix="/api/author_profiles", tags=["author_profiles-controller"])


@router.get(
    "",
    name="api:author_profiles",
    response_model=PaginatedData[AuthorProfileOut],
    summary="Query all AuthorProfile records",
)
async def list_all(
    request: Request,
    response: Response,
    where: Optional[Json] = Query(None),
    order_by: AuthorProfileOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    total = response.headers[
        "x-total-count"
    ] = "%s" % repository.author_profile.find_all(
        pagination, AuthorProfileFilter.from_query(request), order_by, True
    )
    items = repository.author_profile.find_all(
        pagination, AuthorProfileFilter.from_query(request), order_by
    )
    return PaginatedData(
        items=[AuthorProfileOut.from_orm(item) for item in items], total=total
    )


@router.get("/{id}", response_model=AuthorProfileOut, summary="Get AuthorProfile by id")
async def get_by_id(
    id: int = Path(...),
    exclude: Set[str] = Query({}),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.author_profile.find_by_id(id)


@router.post(
    "",
    response_model=AuthorProfileOut,
    status_code=HTTP_201_CREATED,
    summary="Create new AuthorProfile",
)
async def create_new(
    author_profile_in: AuthorProfileIn = Depends(author_profile_in_form),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.author_profile.create(author_profile_in)


@router.put(
    "/{id}", response_model=AuthorProfileOut, summary="Update AuthorProfile by id"
)
async def update(
    author_profile_in: AuthorProfileIn = Depends(author_profile_in_form),
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.author_profile.update(id, author_profile_in)


@router.patch(
    "/{id}",
    response_model=AuthorProfileOut,
    summary="Partial Update AuthorProfile by id",
)
async def patch_update(
    author_profile_in: AuthorProfilePatchBody,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.author_profile.patch(id, author_profile_in)


@router.put(
    "/{id}/file",
    response_model=AuthorProfileOut,
    summary="Update AuthorProfile file by id",
)
async def update_file(
    file: UploadFile = File(...),
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author_profile = repository.author_profile.find_by_id(id)
    author_profile.file = FileInfo(content=file)
    return repository.save(author_profile)


@router.delete(
    "/{id}/file", status_code=HTTP_204_NO_CONTENT, summary="Delete AuthorProfile file"
)
async def delete_file(
    id: int = Path(...), repository: RepositoryManager = Depends(repository_manager)
):
    author_profile = repository.author_profile.find_by_id(id)
    author_profile.file = None
    repository.save(author_profile)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.delete(
    "", status_code=HTTP_204_NO_CONTENT, summary="Delete AuthorProfile by id"
)
async def delete_author_profile(
    request: Request,
    where: Optional[Json] = Query(None),
    repository: RepositoryManager = Depends(repository_manager),
):
    repository.author_profile.delete(AuthorProfileFilter.from_query(request))
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/author",
    response_model=AuthorOutWithoutRelations,
    summary="Get linked author(Author)",
)
async def get_author(
    id: int = Path(...), repository: RepositoryManager = Depends(repository_manager)
):
    author_profile = repository.author_profile.find_by_id(id)
    if author_profile.author is None:
        raise HTTPException(HTTP_404_NOT_FOUND)
    return author_profile.author


@router.put(
    "/{id}/author/{author_id}",
    response_model=AuthorOutWithoutRelations,
    summary="Linked with existing author(Author)",
)
async def link_author(
    id: int = Path(...),
    author_id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    author_profile = repository.author_profile.find_by_id(id)
    author = repository.author.find_by_id(author_id)
    if author_profile.author is not None:
        author_profile.author = None
        repository.save(author_profile)
    author.profile_id = author_profile.id
    return repository.save(author_profile).author


@router.delete(
    "/{id}/author",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete linked author(Author)",
)
async def delete_author(
    id: int = Path(...), repository: RepositoryManager = Depends(repository_manager)
):
    author_profile = repository.author_profile.find_by_id(id)
    author_profile.author = None
    repository.save(author_profile)
    return Response(status_code=HTTP_204_NO_CONTENT)
