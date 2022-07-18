from typing import Optional

from common.admin import BooleanField
from common.admin import FileField as AdminFileField
from common.admin import HasOne, JSONField, NumberField
from pydantic import ValidationError
from starlette.datastructures import FormData

from app.dependencies import repository_manager_ctx
from app.internal.base_models import BaseAdminModel
from app.models.author_profile import (AuthorProfile, AuthorProfileIn,
                                       AuthorProfilePatchBody)
from app.utils import pydantic_error_to_form_validation_error


class AuthorProfileAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
    file = AdminFileField(required=True)
    info = JSONField()
    protected = BooleanField(required=True)
    author = HasOne(identity="author")

    def get_name(self) -> str:
        return "AuthorProfile"

    def identity(self) -> str:
        return "author_profile"

    def datasource(self) -> str:
        return "author_profiles:list"

    def find_by_pk(self, id) -> Optional[AuthorProfile]:
        with repository_manager_ctx() as rm:
            return rm.author_profile.find_by_id(id, False)

    def find_by_pks(self, ids) -> Optional[AuthorProfile]:
        with repository_manager_ctx() as rm:
            return rm.author_profile.find_by_ids(ids)

    def create(self, form_data: FormData):
        with repository_manager_ctx() as rm:
            try:
                _data = self._extract_fields(form_data)
                author_profile_in = AuthorProfileIn(**_data)
                author_profile = rm.author_profile.create(
                    AuthorProfile(**author_profile_in.dict())
                )
                if _data["author"] is not None:
                    author = rm.author.find_by_id(_data["author"])
                    author.profile_id = author_profile.id
                return rm.author_profile.save(author_profile)
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)

    def edit(self, form_data: FormData, id):
        with repository_manager_ctx() as rm:
            try:
                _data = self._extract_fields(form_data, True)
                if _data["_keep_old_file"]:
                    _data.pop("file", None)
                author_profile = rm.author_profile.find_by_id(id)
                author_profile_in = AuthorProfilePatchBody(**_data)
                author_profile.update(author_profile_in.dict())
                if _data["author"] is not None:
                    author = rm.author.find_by_id(_data["author"])
                    if author_profile.author is not None:
                        author_profile.author = None
                        rm.save(author_profile)
                    author.profile_id = author_profile.id
                else:
                    author_profile.author = None
                return rm.author_profile.save(author_profile)
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)
