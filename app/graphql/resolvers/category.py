from typing import List, Optional

from app.filters.category import CategoryFilter, CategoryOrderBy
from app.graphql.response import ListResponse
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.models.category import CategoryIn, CategoryPatchBody


def get_categories(
    _,
    info,
    where: Optional[dict] = None,
    skip=0,
    limit=100,
    order_by: Optional[List[str]] = None,
):
    repository: RepositoryManager = info.context["request"].state.repository
    pagination = PaginationQuery(skip, limit)
    order_by = CategoryOrderBy(order_by)
    if where is not None:
        where = CategoryFilter(**where)
    total = repository.category.find_all(pagination, where, order_by, count=True)
    _list = repository.category.find_all(pagination, where, order_by)
    return ListResponse(total=total, items=_list)


def get_one_category(_, info, id: int):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.category.find_by_id(id)


def create_category(_, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.category.create(CategoryIn(**input))


def update_category(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.category.update(id, CategoryIn(**input))


def patch_category(_, info, id: int, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.category.patch(id, CategoryPatchBody(**input))


def delete_categories(_, info, where: Optional[dict] = None):
    repository: RepositoryManager = info.context["request"].state.repository
    if where is not None:
        where = CategoryFilter(**where)
    return repository.category.delete(where)
