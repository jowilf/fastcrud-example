from typing import TYPE_CHECKING, List, Optional, Union

from fastapi import HTTPException
from starlette.status import HTTP_409_CONFLICT

from app.filters.user import UserFilter, UserOrderBy
from app.internal.base_repository import BaseRepository
from app.internal.filters import PaginationQuery
from app.internal.response import CountResponse
from app.models.user import User, UserIn, UserPatchBody, UserRegister
from app.services.password import hash_password

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class UserRepository(BaseRepository[User]):
    def __init__(self, rm: "RepositoryManager") -> None:
        super().__init__(User, rm.session)
        self.rm = rm

    def find_all(
        self,
        pagination: PaginationQuery = PaginationQuery(),
        where: Optional[UserFilter] = None,
        order_by: Optional[UserOrderBy] = None,
        count=False,
    ) -> Union[List[User], int]:
        return super().find_all(pagination, where, order_by, count)

    def find_one(self, where: Optional[UserFilter]) -> Optional[User]:
        return super().find_one(where)

    def create(self, user_in: UserRegister) -> User:
        if self.find_one(UserFilter(username=user_in.username)) is not None:
            raise HTTPException(
                HTTP_409_CONFLICT,
                detail=[{"loc": ["username"], "msg": f"username already exist."}],
            )
        user_in.password = hash_password(user_in.password)
        user = User(**user_in.dict())
        return self.save(user)

    def update(self, id: int, user_in: UserIn) -> User:
        user = self.find_by_id(id)
        if (
            user.username != user_in.username
            and self.find_one(UserFilter(username=user_in.username)) is not None
        ):
            raise HTTPException(
                HTTP_409_CONFLICT,
                detail=[{"loc": ["username"], "msg": f"username already exist."}],
            )
        user.update(user_in.dict())
        return self.save(user)

    def patch(self, id: int, user_in: UserPatchBody) -> User:
        user = self.find_by_id(id)
        if (
            user_in.username is not None
            and user.username != user_in.username
            and self.find_one(UserFilter(username=user_in.username)) is not None
        ):
            raise HTTPException(
                HTTP_409_CONFLICT,
                detail=[{"loc": ["username"], "msg": f"username already exist."}],
            )
        user.update(user_in.dict(exclude_unset=True))
        return self.save(user)

    def delete(self, where: Optional[UserFilter]) -> CountResponse:
        return super().delete(where)
