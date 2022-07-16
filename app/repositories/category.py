from typing import TYPE_CHECKING, List, Optional, Union

from app.filters.category import CategoryFilter, CategoryOrderBy
from app.internal.base_repository import BaseRepository
from app.internal.filters import PaginationQuery
from app.internal.response import CountResponse
from app.models.category import Category, CategoryIn, CategoryPatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, rm: "RepositoryManager") -> None:
        super().__init__(Category, rm.session)
        self.rm = rm

    def find_all(
        self,
        pagination: PaginationQuery = PaginationQuery(),
        where: Optional[CategoryFilter] = None,
        order_by: Optional[CategoryOrderBy] = None,
        count=False,
    ) -> Union[List[Category], int]:
        return super().find_all(pagination, where, order_by, count)

    def find_one(self, where: Optional[CategoryFilter]) -> Optional[Category]:
        return super().find_one(where)

    def create(self, category_in: CategoryIn) -> Category:
        assert (
            category_in.parent_id is None
            or self.rm.category.find_by_id(category_in.parent_id) is not None
        )
        category = Category(**category_in.dict())
        return self.save(category)

    def update(self, id: int, category_in: CategoryIn) -> Category:
        category = self.find_by_id(id)
        assert (
            category_in.parent_id is None
            or self.rm.category.find_by_id(category_in.parent_id) is not None
        )
        category.update(category_in.dict())
        return self.save(category)

    def patch(self, id: int, category_in: CategoryPatchBody) -> Category:
        category = self.find_by_id(id)
        assert (
            category_in.parent_id is None
            or self.rm.category.find_by_id(category_in.parent_id) is not None
        )
        category.update(category_in.dict(exclude_unset=True))
        return self.save(category)

    def delete(self, where: Optional[CategoryFilter]) -> CountResponse:
        return super().delete(where)
