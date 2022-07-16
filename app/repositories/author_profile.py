from typing import TYPE_CHECKING, List, Optional, Union

from app.filters.author_profile import (AuthorProfileFilter,
                                        AuthorProfileOrderBy)
from app.internal.base_repository import BaseRepository
from app.internal.filters import PaginationQuery
from app.internal.response import CountResponse
from app.models.author_profile import (AuthorProfile, AuthorProfileIn,
                                       AuthorProfilePatchBody)

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class AuthorProfileRepository(BaseRepository[AuthorProfile]):
    def __init__(self, rm: "RepositoryManager") -> None:
        super().__init__(AuthorProfile, rm.session)
        self.rm = rm

    def find_all(
        self,
        pagination: PaginationQuery = PaginationQuery(),
        where: Optional[AuthorProfileFilter] = None,
        order_by: Optional[AuthorProfileOrderBy] = None,
        count=False,
    ) -> Union[List[AuthorProfile], int]:
        return super().find_all(pagination, where, order_by, count)

    def find_one(self, where: Optional[AuthorProfileFilter]) -> Optional[AuthorProfile]:
        return super().find_one(where)

    def create(self, author_profile_in: AuthorProfileIn) -> AuthorProfile:
        author_profile = AuthorProfile(**author_profile_in.dict())
        return self.save(author_profile)

    def update(self, id: int, author_profile_in: AuthorProfileIn) -> AuthorProfile:
        author_profile = self.find_by_id(id)
        author_profile.update(author_profile_in.dict())
        return self.save(author_profile)

    def patch(
        self, id: int, author_profile_in: AuthorProfilePatchBody
    ) -> AuthorProfile:
        author_profile = self.find_by_id(id)
        author_profile.update(author_profile_in.dict(exclude_unset=True))
        return self.save(author_profile)

    def delete(self, where: Optional[AuthorProfileFilter]) -> CountResponse:
        return super().delete(where)
