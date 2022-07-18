from typing import Optional

from common.admin import (DateTimeField, EmailField, NumberField,
                          PasswordField, PhoneField, StringField)
from fastapi import HTTPException
from pydantic import ValidationError
from starlette.datastructures import FormData
from starlette.status import HTTP_409_CONFLICT

from app.dependencies import repository_manager_ctx
from app.filters.user import UserFilter
from app.internal.base_models import BaseAdminModel
from app.models.user import User, UserPatchBody, UserRegister
from app.services.password import hash_password
from app.utils import pydantic_error_to_form_validation_error


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

    def find_by_pk(self, id) -> Optional[User]:
        with repository_manager_ctx() as rm:
            return rm.user.find_by_id(id, False)

    def find_by_pks(self, ids) -> Optional[User]:
        with repository_manager_ctx() as rm:
            return rm.user.find_by_ids(ids)

    def create(self, form_data: FormData):
        with repository_manager_ctx() as rm:
            try:
                _data = self._extract_fields(form_data)
                user_in = UserRegister(**_data)
                if rm.user.find_one(UserFilter(username=user_in.username)) is not None:
                    raise HTTPException(
                        HTTP_409_CONFLICT,
                        detail=[
                            {"loc": ["username"], "msg": f"username already exist."}
                        ],
                    )
                user_in.password = hash_password(user_in.password)
                user = User(**user_in.dict())
                rm.user.save(user)
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)

    def edit(self, form_data: FormData, id):
        with repository_manager_ctx() as rm:
            try:
                _data = self._extract_fields(form_data, True)
                user = rm.user.find_by_id(id)
                user_in = UserPatchBody(**_data)
                if (
                    user.username != user_in.username
                    and rm.user.find_one(UserFilter(username=user_in.username))
                    is not None
                ):
                    raise HTTPException(
                        HTTP_409_CONFLICT,
                        detail=[
                            {"loc": ["username"], "msg": f"username already exist."}
                        ],
                    )
                user.update(user_in.dict())
                rm.user.save(user)
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)
