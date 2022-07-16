from typing import List, Optional

from app.filters.manager import ManagerFilter, ManagerOrderBy
from app.graphql.response import ListResponse
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.models.manager import ManagerIn, ManagerPatchBody


def get_managers(
    _,
    info,
    where: Optional[dict] = None,
    skip=0,
    limit=100,
    order_by: Optional[List[str]] = None,
):
    repository: RepositoryManager = info.context["request"].state.repository
    pagination = PaginationQuery(skip, limit)
    order_by = ManagerOrderBy(order_by)
    if where is not None:
        where = ManagerFilter(**where)
    total = repository.manager.find_all(pagination, where, order_by, count=True)
    _list = repository.manager.find_all(pagination, where, order_by)
    return ListResponse(total=total, items=_list)


def get_one_manager(_, info, id: int):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.manager.find_by_id(id)


def create_manager(_, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.manager.create(ManagerIn(**input))


def update_manager(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.manager.update(id, ManagerIn(**input))


def patch_manager(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.manager.patch(id, ManagerPatchBody(**input))


def delete_managers(_, info, where: Optional[dict] = None):
    repository: RepositoryManager = info.context["request"].state.repository
    if where is not None:
        where = ManagerFilter(**where)
    return repository.manager.delete(where)
