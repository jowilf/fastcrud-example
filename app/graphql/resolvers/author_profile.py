from typing import List, Optional

from app.filters.author_profile import (AuthorProfileFilter,
                                        AuthorProfileOrderBy)
from app.graphql.response import ListResponse
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.models.author_profile import AuthorProfileIn, AuthorProfilePatchBody


def get_author_profiles(
    _,
    info,
    where: Optional[dict] = None,
    skip=0,
    limit=100,
    order_by: Optional[List[str]] = None,
):
    repository: RepositoryManager = info.context["request"].state.repository
    pagination = PaginationQuery(skip, limit)
    order_by = AuthorProfileOrderBy(order_by)
    if where is not None:
        where = AuthorProfileFilter(**where)
    total = repository.author_profile.find_all(pagination, where, order_by, count=True)
    _list = repository.author_profile.find_all(pagination, where, order_by)
    return ListResponse(total=total, items=_list)


def get_one_author_profile(_, info, id: int):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.author_profile.find_by_id(id)


def create_author_profile(_, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.author_profile.create(AuthorProfileIn(**input))


def update_author_profile(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.author_profile.update(id, AuthorProfileIn(**input))


def patch_author_profile(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.author_profile.patch(id, AuthorProfilePatchBody(**input))


def delete_author_profiles(_, info, where: Optional[dict] = None):
    repository: RepositoryManager = info.context["request"].state.repository
    if where is not None:
        where = AuthorProfileFilter(**where)
    return repository.author_profile.delete(where)
