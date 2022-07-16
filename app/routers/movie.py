from typing import List, Optional, Set

from fastapi import (APIRouter, Depends, HTTPException, Path, Query, Request,
                     Response)
from pydantic import Json
from starlette.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                              HTTP_404_NOT_FOUND)

from app.dependencies import repository_manager
from app.filters.author import AuthorFilter, AuthorOrderBy
from app.filters.movie import AnyMovieFilter, MovieFilter, MovieOrderBy
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.internal.response import PaginatedData
from app.models.author import Author, AuthorInBase, AuthorOutWithoutRelations
from app.models.category import CategoryOutWithoutRelations
from app.models.movie import MovieIn, MovieOut, MoviePatchBody
from app.models.movie_preview import MoviePreviewOutWithoutRelations

router = APIRouter(prefix="/api/movies", tags=["movies-controller"])


@router.get(
    "",
    name="api:movies",
    response_model=PaginatedData[MovieOut],
    summary="Query all Movie records",
)
async def list_all(
    request: Request,
    response: Response,
    where: Optional[Json] = Query(None),
    order_by: MovieOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    total = response.headers["x-total-count"] = "%s" % repository.movie.find_all(
        pagination, MovieFilter.from_query(request), order_by, True
    )
    items = repository.movie.find_all(
        pagination, MovieFilter.from_query(request), order_by
    )
    return PaginatedData(items=[MovieOut.from_orm(item) for item in items], total=total)


@router.get("/{id}", response_model=MovieOut, summary="Get Movie by id")
async def get_by_id(
    id: int = Path(...),
    exclude: Set[str] = Query({}),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.movie.find_by_id(id)


@router.post(
    "",
    response_model=MovieOut,
    status_code=HTTP_201_CREATED,
    summary="Create new Movie",
)
async def create_new(
    movie_in: MovieIn, repository: RepositoryManager = Depends(repository_manager)
):
    return repository.movie.create(movie_in)


@router.put("/{id}", response_model=MovieOut, summary="Update Movie by id")
async def update(
    movie_in: MovieIn,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.movie.update(id, movie_in)


@router.patch("/{id}", response_model=MovieOut, summary="Partial Update Movie by id")
async def patch_update(
    movie_in: MoviePatchBody,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.movie.patch(id, movie_in)


@router.delete("", status_code=HTTP_204_NO_CONTENT, summary="Delete Movie by id")
async def delete_movie(
    request: Request,
    where: Optional[Json] = Query(None),
    repository: RepositoryManager = Depends(repository_manager),
):
    repository.movie.delete(MovieFilter.from_query(request))
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/preview",
    response_model=MoviePreviewOutWithoutRelations,
    summary="Get linked preview(MoviePreview)",
)
async def get_preview(
    id: int = Path(...), repository: RepositoryManager = Depends(repository_manager)
):
    movie = repository.movie.find_by_id(id)
    if movie.preview is None:
        raise HTTPException(HTTP_404_NOT_FOUND)
    return movie.preview


@router.put(
    "/{id}/preview/{preview_id}",
    response_model=MoviePreviewOutWithoutRelations,
    summary="Linked with existing preview(MoviePreview)",
)
async def link_preview(
    id: int = Path(...),
    preview_id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    movie = repository.movie.find_by_id(id)
    preview = repository.movie_preview.find_by_id(preview_id)
    if movie.preview is not None:
        movie.preview = None
        repository.save(movie)
    preview.movie_id = movie.id
    return repository.save(movie).preview


@router.delete(
    "/{id}/preview",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete linked preview(MoviePreview)",
)
async def delete_preview(
    id: int = Path(...), repository: RepositoryManager = Depends(repository_manager)
):
    movie = repository.movie.find_by_id(id)
    movie.preview = None
    repository.save(movie)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/category",
    response_model=CategoryOutWithoutRelations,
    summary="Get linked category(Category)",
)
async def get_category(
    id: int = Path(...), repository: RepositoryManager = Depends(repository_manager)
):
    movie = repository.movie.find_by_id(id)
    if movie.category is None:
        raise HTTPException(HTTP_404_NOT_FOUND)
    return movie.category


@router.put(
    "/{id}/category/{category_id}",
    response_model=CategoryOutWithoutRelations,
    summary="Linked with existing category(Category)",
)
async def link_category(
    id: int = Path(...),
    category_id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    movie = repository.movie.find_by_id(id)
    movie.category_id = repository.category.find_by_id(category_id).id
    return repository.save(movie).category


@router.delete(
    "/{id}/category",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete linked category(Category)",
)
async def delete_category(
    id: int = Path(...), repository: RepositoryManager = Depends(repository_manager)
):
    movie = repository.movie.find_by_id(id)
    movie.category = None
    repository.save(movie)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/authors",
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
    where.movies = AnyMovieFilter(id=id)
    total = repository.author.find_all(pagination, where, order_by, count=True)
    items = repository.author.find_all(pagination, where, order_by)
    return PaginatedData(
        items=[AuthorOutWithoutRelations.from_orm(item) for item in items], total=total
    )


@router.post(
    "/{id}/authors",
    response_model=AuthorOutWithoutRelations,
    status_code=HTTP_201_CREATED,
    summary="Add authors(Author)",
)
async def add_authors(
    author_in: AuthorInBase,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    movie = repository.movie.find_by_id(id)
    new_author = Author(**author_in.dict())
    movie.authors.append(new_author)
    return repository.save(new_author)


@router.put(
    "/{id}/authors",
    response_model=List[AuthorOutWithoutRelations],
    summary="Set authors(Author) by ids",
)
async def set_existing_authors(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    movie = repository.movie.find_by_id(id)
    movie.authors = repository.author.find_by_ids(ids)
    repository.save(movie)
    return repository.author.find_by_ids(ids)


@router.patch(
    "/{id}/authors",
    response_model=List[AuthorOutWithoutRelations],
    summary="Add authors(Author) by ids",
)
async def add_existing_authors(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    movie = repository.movie.find_by_id(id)
    movie.authors.extend(repository.author.find_by_ids(ids))
    repository.save(movie)
    return repository.author.find_by_ids(ids)
