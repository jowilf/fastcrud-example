from typing import Optional

from common.admin import (DateField, DateTimeField, HasMany, HasOne,
                          NumberField, StringField, TextField)
from pydantic import ValidationError
from starlette.datastructures import FormData

from app.dependencies import repository_manager_ctx
from app.internal.base_models import BaseAdminModel
from app.models.movie import Movie, MovieIn, MoviePatchBody
from app.utils import pydantic_error_to_form_validation_error


class MovieAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
    name = StringField(required=True)
    description = TextField()
    watch_count = NumberField()
    tags = StringField(is_array=True)
    release_date = DateField()
    created_at = DateTimeField(exclude_from_create=True, exclude_from_edit=True)
    updated_at = DateTimeField(exclude_from_create=True, exclude_from_edit=True)
    preview = HasOne(identity="movie_preview")
    category = HasOne(identity="category")
    authors = HasMany(identity="author")

    def get_name(self) -> str:
        return "Movie"

    def identity(self) -> str:
        return "movie"

    def datasource(self) -> str:
        return "movies:list"

    def find_by_pk(self, id) -> Optional[Movie]:
        with repository_manager_ctx() as rm:
            return rm.movie.find_by_id(id, False)

    def find_by_pks(self, ids) -> Optional[Movie]:
        with repository_manager_ctx() as rm:
            return rm.movie.find_by_ids(ids)

    def create(self, form_data: FormData):
        with repository_manager_ctx() as rm:
            try:
                _data = self._extract_fields(form_data)
                movie_in = MovieIn(**_data)
                movie = Movie(**movie_in.dict())
                if _data["preview"] is not None:
                    preview = rm.movie_preview.find_by_id(_data["preview"])
                    preview.movie_id = movie.id
                if _data["category"] is not None:
                    movie.category_id = rm.category.find_by_id(_data["category"]).id
                if len(_data["authors"]) > 0:
                    movie.authors = rm.author.find_by_ids(_data["authors"])
                rm.movie.save(movie)
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)

    def edit(self, form_data: FormData, id):
        with repository_manager_ctx() as rm:
            try:
                _data = self._extract_fields(form_data, True)
                movie = rm.movie.find_by_id(id)
                movie_in = MoviePatchBody(**_data)
                movie.update(movie_in.dict())
                if _data["preview"] is not None:
                    preview = rm.movie_preview.find_by_id(_data["preview"])
                    if movie.preview is not None:
                        movie.preview = None
                        rm.save(movie)
                    preview.movie_id = movie.id
                else:
                    movie.preview = None
                if _data["category"] is not None:
                    movie.category_id = rm.category.find_by_id(_data["category"]).id
                else:
                    movie.category = None
                movie.authors = rm.author.find_by_ids(_data["authors"])
                rm.movie.save(movie)
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)
