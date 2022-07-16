from typing import TYPE_CHECKING, Optional

from common.admin import BooleanField
from common.admin import FileField as AdminFileField
from common.admin import HasOne, JSONField
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models.author_profile import (AuthorProfile, AuthorProfileIn,
                                       AuthorProfilePatchBody)

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class AuthorProfileAdmin(BaseAdminModel):
    file = AdminFileField(required=True)
    info = JSONField()
    protected = BooleanField(required=True)
    author = HasOne(identity="author")

    def get_name(self) -> str:
        return "AuthorProfile"

    def identity(self) -> str:
        return "author_profile"

    def datasource(self) -> str:
        return "api:author_profiles"

    def find_by_id(self, rm: "RepositoryManager", id) -> Optional[AuthorProfile]:
        return rm.author_profile.find_by_id(id, False)

    def create(self, rm: "RepositoryManager", form_data: FormData):
        _data = self._extract_fields(form_data)
        author_profile_in = AuthorProfileIn(**_data)
        author_profile = AuthorProfile(**author_profile_in.dict())
        if _data["author"] is not None:
            author = rm.author.find_by_id(_data["author"])
            author.profile_id = author_profile.id
        rm.author_profile.save(author_profile)

    def edit(self, rm: "RepositoryManager", form_data: FormData, id):
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
        rm.author_profile.save(author_profile)
