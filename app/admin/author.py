from typing import TYPE_CHECKING, Optional

from common.admin import (DateField, DateTimeField, EnumField, HasMany, HasOne,
                          NumberField, StringField, TimeField)
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models import enums
from app.models.author import Author, AuthorIn, AuthorPatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class AuthorAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
    lastname = StringField(required=True)
    firstname = StringField(required=True)
    sex = EnumField(type=enums.Gender)
    birthday = DateField()
    wakeup_time = TimeField()
    wakeup_day = DateTimeField()
    created_at = DateTimeField(exclude_from_create=True, exclude_from_edit=True)
    updated_at = DateTimeField(exclude_from_create=True, exclude_from_edit=True)
    profile = HasOne(identity="author_profile")
    manager = HasOne(identity="manager")
    movies = HasMany(identity="movie")
    friends = HasMany(identity="author")
    friends_of = HasMany(identity="author")

    def __init__(self, rm: "RepositoryManager" = None):
        self.rm = rm

    def get_name(self) -> str:
        return "Author"

    def identity(self) -> str:
        return "author"

    def datasource(self) -> str:
        return "api:authors"

    def find_by_pk(self, id) -> Optional[Author]:
        return self.rm.author.find_by_id(id, False)

    def create(self, form_data: FormData):
        _data = self._extract_fields(form_data)
        author_in = AuthorIn(**_data)
        author = Author(**author_in.dict())
        if _data["profile"] is not None:
            profile = self.rm.author_profile.find_by_id(_data["profile"])
            if profile.author is not None:
                profile.author = None
                self.rm.save(profile)
            author.profile_id = profile.id
        if _data["manager"] is not None:
            author.manager_id = self.rm.manager.find_by_id(_data["manager"]).id
        if len(_data["movies"]) > 0:
            author.movies = self.rm.movie.find_by_ids(_data["movies"])
        if len(_data["friends"]) > 0:
            author.friends = self.rm.author.find_by_ids(_data["friends"])
        if len(_data["friends_of"]) > 0:
            author.friends_of = self.rm.author.find_by_ids(_data["friends_of"])
        self.rm.author.save(author)

    def edit(self, form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        author = self.rm.author.find_by_id(id)
        author_in = AuthorPatchBody(**_data)
        author.update(author_in.dict())
        if _data["profile"] is not None:
            profile = self.rm.author_profile.find_by_id(_data["profile"])
            if profile.author is not None:
                profile.author = None
                self.rm.save(profile)
            author.profile_id = profile.id
        else:
            author.profile = None
        if _data["manager"] is not None:
            author.manager_id = self.rm.manager.find_by_id(_data["manager"]).id
        else:
            author.manager = None
        author.movies = self.rm.movie.find_by_ids(_data["movies"])
        author.friends = self.rm.author.find_by_ids(_data["friends"])
        author.friends_of = self.rm.author.find_by_ids(_data["friends_of"])
        self.rm.author.save(author)
