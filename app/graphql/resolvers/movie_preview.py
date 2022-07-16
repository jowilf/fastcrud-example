from typing import List, Optional

from app.filters.movie_preview import MoviePreviewFilter, MoviePreviewOrderBy
from app.graphql.response import ListResponse
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.models.movie_preview import MoviePreviewIn, MoviePreviewPatchBody


def get_movie_previews(
    _,
    info,
    where: Optional[dict] = None,
    skip=0,
    limit=100,
    order_by: Optional[List[str]] = None,
):
    repository: RepositoryManager = info.context["request"].state.repository
    pagination = PaginationQuery(skip, limit)
    order_by = MoviePreviewOrderBy(order_by)
    if where is not None:
        where = MoviePreviewFilter(**where)
    total = repository.movie_preview.find_all(pagination, where, order_by, count=True)
    _list = repository.movie_preview.find_all(pagination, where, order_by)
    return ListResponse(total=total, items=_list)


def get_one_movie_preview(_, info, id: int):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.movie_preview.find_by_id(id)


def create_movie_preview(_, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.movie_preview.create(MoviePreviewIn(**input))


def update_movie_preview(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.movie_preview.update(id, MoviePreviewIn(**input))


def patch_movie_preview(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.movie_preview.patch(id, MoviePreviewPatchBody(**input))


def delete_movie_previews(_, info, where: Optional[dict] = None):
    repository: RepositoryManager = info.context["request"].state.repository
    if where is not None:
        where = MoviePreviewFilter(**where)
    return repository.movie_preview.delete(where)
