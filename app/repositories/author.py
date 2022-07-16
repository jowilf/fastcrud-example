from typing import TYPE_CHECKING, List, Optional, Union

from app.filters.author import AuthorFilter, AuthorOrderBy
from app.internal.base_repository import BaseRepository
from app.internal.filters import PaginationQuery
from app.internal.response import CountResponse
from app.models.author import Author, AuthorIn, AuthorPatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class AuthorRepository(BaseRepository[Author]):
    def __init__(self, rm: "RepositoryManager") -> None:
        super().__init__(Author, rm.session)
        self.rm = rm

    def find_all(
        self,
        pagination: PaginationQuery = PaginationQuery(),
        where: Optional[AuthorFilter] = None,
        order_by: Optional[AuthorOrderBy] = None,
        count=False,
    ) -> Union[List[Author], int]:
        return super().find_all(pagination, where, order_by, count)

    def find_one(self, where: Optional[AuthorFilter]) -> Optional[Author]:
        return super().find_one(where)

    def create(self, author_in: AuthorIn) -> Author:
        assert (
            author_in.manager_id is None
            or self.rm.manager.find_by_id(author_in.manager_id) is not None
        )
        if author_in.profile_id is not None:
            profile = self.rm.author_profile.find_by_id(author_in.profile_id)
            profile.author = None
            self.rm.save(profile)
        author = Author(**author_in.dict())
        return self.save(author)

    def update(self, id: int, author_in: AuthorIn) -> Author:
        author = self.find_by_id(id)
        assert (
            author_in.manager_id is None
            or self.rm.manager.find_by_id(author_in.manager_id) is not None
        )
        if author_in.profile_id is not None:
            profile = self.rm.author_profile.find_by_id(author_in.profile_id)
            profile.author = None
            self.rm.save(profile)
        author.update(author_in.dict())
        return self.save(author)

    def patch(self, id: int, author_in: AuthorPatchBody) -> Author:
        author = self.find_by_id(id)
        assert (
            author_in.manager_id is None
            or self.rm.manager.find_by_id(author_in.manager_id) is not None
        )
        if author_in.profile_id is not None:
            profile = self.rm.author_profile.find_by_id(author_in.profile_id)
            profile.author = None
            self.rm.save(profile)
        author.update(author_in.dict(exclude_unset=True))
        return self.save(author)

    def delete(self, where: Optional[AuthorFilter]) -> CountResponse:
        return super().delete(where)
