from typing import List, Optional

from app.filters.user import UserFilter, UserOrderBy
from app.graphql.response import ListResponse
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.models.user import UserIn, UserPatchBody, UserRegister


def get_users(
    _,
    info,
    where: Optional[dict] = None,
    skip=0,
    limit=100,
    order_by: Optional[List[str]] = None,
):
    repository: RepositoryManager = info.context["request"].state.repository
    pagination = PaginationQuery(skip, limit)
    order_by = UserOrderBy(order_by)
    if where is not None:
        where = UserFilter(**where)
    total = repository.user.find_all(pagination, where, order_by, count=True)
    _list = repository.user.find_all(pagination, where, order_by)
    return ListResponse(total=total, items=_list)


def get_one_user(_, info, id: int):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.user.find_by_id(id)


def create_user(_, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.user.create(UserRegister(**input))


def update_user(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.user.update(id, UserIn(**input))


def patch_user(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.user.patch(id, UserPatchBody(**input))


def delete_users(_, info, where: Optional[dict] = None):
    repository: RepositoryManager = info.context["request"].state.repository
    if where is not None:
        where = UserFilter(**where)
    return repository.user.delete(where)
