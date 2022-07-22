from typing import List, Optional, Set

from common.types import FileInfo
from fastapi import (APIRouter, Depends, File, HTTPException, Path, Query,
                     Request, Response, UploadFile)
from pydantic import Json
from starlette.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                              HTTP_404_NOT_FOUND)

from app.dependencies import repository_manager
from app.filters.movie_preview import MoviePreviewFilter, MoviePreviewOrderBy
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.internal.response import PaginatedData
from app.models.movie import MovieOutWithoutRelations
from app.models.movie_preview import (MoviePreviewIn, MoviePreviewOut,
                                      MoviePreviewPatchBody,
                                      movie_preview_in_form)
from app.models.user import User
from app.services.auth import authorize

router = APIRouter(prefix="/api/movie_previews", tags=["movie_previews-controller"])


@router.get(
    "",
    name="movie_previews:list",
    response_model=PaginatedData[MoviePreviewOut],
    summary="Query all MoviePreview records",
)
async def list_all(
    request: Request,
    response: Response,
    where: Optional[Json] = Query(None),
    order_by: MoviePreviewOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    total = repository.movie_preview.find_all(
        pagination, MoviePreviewFilter.from_query(request), order_by, True
    )
    items = repository.movie_preview.find_all(
        pagination, MoviePreviewFilter.from_query(request), order_by
    )
    return PaginatedData(
        items=[MoviePreviewOut.from_orm(item) for item in items], total=total
    )


@router.get(
    "/{id}",
    name="movie_previews:get",
    response_model=MoviePreviewOut,
    summary="Get MoviePreview by id",
)
async def get_by_id(
    id: int = Path(...),
    exclude: Set[str] = Query({}),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.movie_preview.find_by_id(id)


@router.post(
    "",
    name="movie_previews:create",
    response_model=MoviePreviewOut,
    status_code=HTTP_201_CREATED,
    summary="Create new MoviePreview",
)
async def create_new(
    movie_preview_in: MoviePreviewIn = Depends(movie_preview_in_form),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.movie_preview.create(movie_preview_in)


@router.put(
    "/{id}",
    name="movie_previews:update",
    response_model=MoviePreviewOut,
    summary="Update MoviePreview by id",
)
async def update(
    movie_preview_in: MoviePreviewIn = Depends(movie_preview_in_form),
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie_preview:edit"])),
):
    return repository.movie_preview.update(id, movie_preview_in)


@router.patch(
    "/{id}",
    name="movie_previews:patch",
    response_model=MoviePreviewOut,
    summary="Partial Update MoviePreview by id",
)
async def patch_update(
    movie_preview_in: MoviePreviewPatchBody,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie_preview:edit"])),
):
    return repository.movie_preview.patch(id, movie_preview_in)


@router.put(
    "/{id}/images",
    name="movie_previews:images:update",
    response_model=MoviePreviewOut,
    summary="Update MoviePreview images by id",
)
async def update_images(
    images: Optional[List[UploadFile]] = File([]),
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie_preview:edit"])),
):
    movie_preview = repository.movie_preview.find_by_id(id)
    movie_preview.images = [FileInfo(content=_f) for _f in images]
    return repository.save(movie_preview)


@router.delete(
    "/{id}/images",
    name="movie_previews:images:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete MoviePreview images",
)
async def delete_images(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie_preview:edit"])),
):
    movie_preview = repository.movie_preview.find_by_id(id)
    movie_preview.images = None
    repository.save(movie_preview)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.delete(
    "",
    name="movie_previews:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete MoviePreview by id",
)
async def delete_movie_preview(
    request: Request,
    where: Optional[Json] = Query(None),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie_preview:delete"])),
):
    repository.movie_preview.delete(MoviePreviewFilter.from_query(request))
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/movie",
    name="movie_previews:movie:get",
    response_model=MovieOutWithoutRelations,
    summary="Get linked movie(Movie)",
)
async def get_movie(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    movie_preview = repository.movie_preview.find_by_id(id)
    if movie_preview.movie is None:
        raise HTTPException(HTTP_404_NOT_FOUND)
    return movie_preview.movie


@router.put(
    "/{id}/movie/{movie_id}",
    name="movie_previews:movie:put",
    response_model=MovieOutWithoutRelations,
    summary="Linked with movie(Movie) by id",
)
async def link_movie(
    id: int = Path(...),
    movie_id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie_preview:edit"])),
):
    movie_preview = repository.movie_preview.find_by_id(id)
    movie = repository.movie.find_by_id(movie_id)
    if movie.preview is not None:
        movie.preview = None
        repository.save(movie)
    movie_preview.movie_id = movie.id
    return repository.save(movie_preview).movie


@router.delete(
    "/{id}/movie",
    name="movie_previews:movie:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete linked movie(Movie)",
)
async def delete_movie(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie_preview:edit"])),
):
    movie_preview = repository.movie_preview.find_by_id(id)
    movie_preview.movie = None
    repository.save(movie_preview)
    return Response(status_code=HTTP_204_NO_CONTENT)
