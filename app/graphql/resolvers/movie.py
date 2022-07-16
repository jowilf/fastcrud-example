from typing import List, Optional

from app.filters.movie import MovieFilter, MovieOrderBy
from app.graphql.response import ListResponse
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.models.movie import MovieIn, MoviePatchBody


def get_movies(
    _,
    info,
    where: Optional[dict] = None,
    skip=0,
    limit=100,
    order_by: Optional[List[str]] = None,
):
    repository: RepositoryManager = info.context["request"].state.repository
    pagination = PaginationQuery(skip, limit)
    order_by = MovieOrderBy(order_by)
    if where is not None:
        where = MovieFilter(**where)
    total = repository.movie.find_all(pagination, where, order_by, count=True)
    _list = repository.movie.find_all(pagination, where, order_by)
    return ListResponse(total=total, items=_list)


def get_one_movie(_, info, id: int):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.movie.find_by_id(id)


def create_movie(_, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.movie.create(MovieIn(**input))


def update_movie(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.movie.update(id, MovieIn(**input))


def patch_movie(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.movie.patch(id, MoviePatchBody(**input))


def delete_movies(_, info, where: Optional[dict] = None):
    repository: RepositoryManager = info.context["request"].state.repository
    if where is not None:
        where = MovieFilter(**where)
    return repository.movie.delete(where)
