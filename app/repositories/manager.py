from typing import TYPE_CHECKING, List, Optional, Union

from app.filters.manager import ManagerFilter, ManagerOrderBy
from app.internal.base_repository import BaseRepository
from app.internal.filters import PaginationQuery
from app.internal.response import CountResponse
from app.models.manager import Manager, ManagerIn, ManagerPatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class ManagerRepository(BaseRepository[Manager]):
    def __init__(self, rm: "RepositoryManager") -> None:
        super().__init__(Manager, rm.session)
        self.rm = rm

    def find_all(
        self,
        pagination: PaginationQuery = PaginationQuery(),
        where: Optional[ManagerFilter] = None,
        order_by: Optional[ManagerOrderBy] = None,
        count=False,
    ) -> Union[List[Manager], int]:
        return super().find_all(pagination, where, order_by, count)

    def find_one(self, where: Optional[ManagerFilter]) -> Optional[Manager]:
        return super().find_one(where)

    def create(self, manager_in: ManagerIn) -> Manager:
        manager = Manager(**manager_in.dict())
        return self.save(manager)

    def update(self, id: int, manager_in: ManagerIn) -> Manager:
        manager = self.find_by_id(id)
        manager.update(manager_in.dict())
        return self.save(manager)

    def patch(self, id: int, manager_in: ManagerPatchBody) -> Manager:
        manager = self.find_by_id(id)
        manager.update(manager_in.dict(exclude_unset=True))
        return self.save(manager)

    def delete(self, where: Optional[ManagerFilter]) -> CountResponse:
        return super().delete(where)
