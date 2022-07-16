from typing import TYPE_CHECKING, Optional

from common.admin import (DateTimeField, EmailField, PasswordField, PhoneField,
                          StringField)
from fastapi import HTTPException
from starlette.datastructures import FormData
from starlette.status import HTTP_409_CONFLICT

from app.filters.user import UserFilter
from app.internal.base_models import BaseAdminModel
from app.models.user import User, UserPatchBody, UserRegister
from app.services.password import hash_password

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class UserAdmin(BaseAdminModel):
    username = StringField(required=True)
    phonenumber = PhoneField()
    email = EmailField()
    password = PasswordField(
        min_length=8,
        max_length=20,
        has_uppercase=True,
        has_lowercase=True,
        min_digits=1,
        allow_spaces=False,
        special_chars="@&%$()=!?*+-.,:;",
        required=True,
    )
    roles = StringField(is_array=True)
    date_joined = DateTimeField(exclude_from_create=True, exclude_from_edit=True)

    def get_name(self) -> str:
        return "User"

    def identity(self) -> str:
        return "user"

    def datasource(self) -> str:
        return "api:users"

    def find_by_id(self, rm: "RepositoryManager", id) -> Optional[User]:
        return rm.user.find_by_id(id, False)

    def create(self, rm: "RepositoryManager", form_data: FormData):
        _data = self._extract_fields(form_data)
        user_in = UserRegister(**_data)
        if rm.user.find_one(UserFilter(username=user_in.username)) is not None:
            raise HTTPException(
                HTTP_409_CONFLICT,
                detail=[{"loc": ["username"], "msg": f"username already exist."}],
            )
        user_in.password = hash_password(user_in.password)
        user = User(**user_in.dict())
        rm.user.save(user)

    def edit(self, rm: "RepositoryManager", form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        user = rm.user.find_by_id(id)
        user_in = UserPatchBody(**_data)
        if (
            user.username != user_in.username
            and rm.user.find_one(UserFilter(username=user_in.username)) is not None
        ):
            raise HTTPException(
                HTTP_409_CONFLICT,
                detail=[{"loc": ["username"], "msg": f"username already exist."}],
            )
        user.update(user_in.dict())
        rm.user.save(user)
