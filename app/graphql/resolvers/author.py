from typing import List, Optional

from app.filters.author import AuthorFilter, AuthorOrderBy
from app.graphql.response import ListResponse
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.models.author import AuthorIn, AuthorPatchBody


def get_authors(
    _,
    info,
    where: Optional[dict] = None,
    skip=0,
    limit=100,
    order_by: Optional[List[str]] = None,
):
    repository: RepositoryManager = info.context["request"].state.repository
    pagination = PaginationQuery(skip, limit)
    order_by = AuthorOrderBy(order_by)
    if where is not None:
        where = AuthorFilter(**where)
    total = repository.author.find_all(pagination, where, order_by, count=True)
    _list = repository.author.find_all(pagination, where, order_by)
    return ListResponse(total=total, items=_list)


def get_one_author(_, info, id: int):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.author.find_by_id(id)


def create_author(_, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.author.create(AuthorIn(**input))


def update_author(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.author.update(id, AuthorIn(**input))


def patch_author(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.author.patch(id, AuthorPatchBody(**input))


def delete_authors(_, info, where: Optional[dict] = None):
    repository: RepositoryManager = info.context["request"].state.repository
    if where is not None:
        where = AuthorFilter(**where)
    return repository.author.delete(where)
