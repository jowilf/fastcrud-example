from typing import TYPE_CHECKING, Optional

from pydantic import ValidationError
from sf_admin import (DateField, DateTimeField, EnumField, HasMany, HasOne,
                      NumberField, TextField, TimeField)
from starlette.datastructures import FormData
from starlette.requests import Request

from app.internal.base_models import BaseAdminModel
from app.models import enums
from app.models.author import Author, AuthorIn, AuthorPatchBody
from app.utils import pydantic_error_to_form_validation_error

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class AuthorAdmin(BaseAdminModel):
    id = NumberField(exclude_from_create=True, exclude_from_edit=True)
    lastname = TextField(required=True)
    firstname = TextField(required=True)
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

    def get_name(self) -> str:
        return "Author"

    def identity(self) -> str:
        return "author"

    def datasource(self) -> str:
        return "authors:list"

    def find_by_pk(self, request: Request, id) -> Optional[Author]:
        rm: RepositoryManager = request.state.rm
        return rm.author.find_by_id(id, False)

    def find_by_pks(self, request: Request, ids) -> Optional[Author]:
        rm: RepositoryManager = request.state.rm
        return rm.author.find_by_ids(ids)

    def create(self, request: Request, form_data: FormData):
        rm: RepositoryManager = request.state.rm
        try:
            _data = self._extract_fields(form_data)
            author_in = AuthorIn(**_data)
            author = rm.author.create(author_in)
            if _data["profile"] is not None:
                profile = rm.author_profile.find_by_id(_data["profile"])
                if profile.author is not None:
                    profile.author = None
                    rm.save(profile)
                author.profile_id = profile.id
            if _data["manager"] is not None:
                author.manager_id = rm.manager.find_by_id(_data["manager"]).id
            if len(_data["movies"]) > 0:
                author.movies = rm.movie.find_by_ids(_data["movies"])
            if len(_data["friends"]) > 0:
                author.friends = rm.author.find_by_ids(_data["friends"])
            if len(_data["friends_of"]) > 0:
                author.friends_of = rm.author.find_by_ids(_data["friends_of"])
            return rm.author.save(author)
        except ValidationError as exc:
            raise pydantic_error_to_form_validation_error(exc)

    def edit(self, request: Request, form_data: FormData, id):
        rm: RepositoryManager = request.state.rm
        try:
            _data = self._extract_fields(form_data, True)
            author = rm.author.find_by_id(id)
            author_in = AuthorPatchBody(**_data)
            author.update(author_in.dict())
            if _data["profile"] is not None:
                profile = rm.author_profile.find_by_id(_data["profile"])
                if profile.author is not None:
                    profile.author = None
                    rm.save(profile)
                author.profile_id = profile.id
            else:
                author.profile = None
            if _data["manager"] is not None:
                author.manager_id = rm.manager.find_by_id(_data["manager"]).id
            else:
                author.manager = None
            author.movies = rm.movie.find_by_ids(_data["movies"])
            author.friends = rm.author.find_by_ids(_data["friends"])
            author.friends_of = rm.author.find_by_ids(_data["friends_of"])
            return rm.author.save(author)
        except ValidationError as exc:
            raise pydantic_error_to_form_validation_error(exc)
