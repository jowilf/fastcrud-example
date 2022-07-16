from typing import TYPE_CHECKING, Optional

from common.admin import BooleanField
from common.admin import FileField as AdminFileField
from common.admin import HasOne, JSONField, NumberField
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models.author_profile import (AuthorProfile, AuthorProfileIn,
                                       AuthorProfilePatchBody)

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class AuthorProfileAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
    file = AdminFileField(required=True)
    info = JSONField()
    protected = BooleanField(required=True)
    author = HasOne(identity="author")

    def __init__(self, rm: "RepositoryManager" = None):
        self.rm = rm

    def get_name(self) -> str:
        return "AuthorProfile"

    def identity(self) -> str:
        return "author_profile"

    def datasource(self) -> str:
        return "api:author_profiles"

    def find_by_pk(self, id) -> Optional[AuthorProfile]:
        return self.rm.author_profile.find_by_id(id, False)

    def create(self, form_data: FormData):
        _data = self._extract_fields(form_data)
        author_profile_in = AuthorProfileIn(**_data)
        author_profile = AuthorProfile(**author_profile_in.dict())
        if _data["author"] is not None:
            author = self.rm.author.find_by_id(_data["author"])
            author.profile_id = author_profile.id
        self.rm.author_profile.save(author_profile)

    def edit(self, form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        if _data["_keep_old_file"]:
            _data.pop("file", None)
        author_profile = self.rm.author_profile.find_by_id(id)
        author_profile_in = AuthorProfilePatchBody(**_data)
        author_profile.update(author_profile_in.dict())
        if _data["author"] is not None:
            author = self.rm.author.find_by_id(_data["author"])
            if author_profile.author is not None:
                author_profile.author = None
                self.rm.save(author_profile)
            author.profile_id = author_profile.id
        else:
            author_profile.author = None
        self.rm.author_profile.save(author_profile)
