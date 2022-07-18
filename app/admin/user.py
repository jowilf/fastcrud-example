from typing import TYPE_CHECKING, Optional

from common.admin import (DateTimeField, EmailField, NumberField,
                          PasswordField, PhoneField, StringField)
from common.admin.exceptions import FormValidationError
from fastapi import HTTPException
from pydantic import ValidationError
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.status import HTTP_409_CONFLICT

from app.filters.user import UserFilter
from app.internal.base_models import BaseAdminModel
from app.models.user import User, UserPatchBody, UserRegister
from app.services.password import hash_password
from app.utils import pydantic_error_to_form_validation_error

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class UserAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
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
    date_joined = DateTimeField(exclude_from_create=True, exclude_from_edit=True)
    roles = StringField(is_array=True)
    is_superuser = StringField(exclude_from_create=True, exclude_from_edit=True)

    def get_name(self) -> str:
        return "User"

    def identity(self) -> str:
        return "user"

    def datasource(self) -> str:
        return "users:list"

    def find_by_pk(self, request: Request, id) -> Optional[User]:
        rm: RepositoryManager = request.state.rm
        return rm.user.find_by_id(id, False)

    def find_by_pks(self, request: Request, ids) -> Optional[User]:
        rm: RepositoryManager = request.state.rm
        return rm.user.find_by_ids(ids)

    def create(self, request: Request, form_data: FormData):
        rm: RepositoryManager = request.state.rm
        try:
            _data = self._extract_fields(form_data)
            user_in = UserRegister(**_data)
            if rm.user.find_one(UserFilter(username=user_in.username)) is not None:
                raise FormValidationError({"username": f"username already exist."})
            user_in.password = hash_password(user_in.password)
            user = rm.user.create(user_in)
            return user
        except ValidationError as exc:
            raise pydantic_error_to_form_validation_error(exc)

    def edit(self, request: Request, form_data: FormData, id):
        rm: RepositoryManager = request.state.rm
        try:
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
            return rm.user.save(user)
        except ValidationError as exc:
            raise pydantic_error_to_form_validation_error(exc)
