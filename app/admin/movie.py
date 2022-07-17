from typing import TYPE_CHECKING, Optional

from common.admin import (DateField, DateTimeField, HasMany, HasOne,
                          NumberField, StringField, TextField)
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models.movie import Movie, MovieIn, MoviePatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


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

    def __init__(self, rm: "RepositoryManager" = None):
        self.rm = rm

    def get_name(self) -> str:
        return "Movie"

    def identity(self) -> str:
        return "movie"

    def datasource(self) -> str:
        return "movies:list"

    def find_by_pk(self, id) -> Optional[Movie]:
        return self.rm.movie.find_by_id(id, False)

    def create(self, form_data: FormData):
        _data = self._extract_fields(form_data)
        movie_in = MovieIn(**_data)
        movie = Movie(**movie_in.dict())
        if _data["preview"] is not None:
            preview = self.rm.movie_preview.find_by_id(_data["preview"])
            preview.movie_id = movie.id
        if _data["category"] is not None:
            movie.category_id = self.rm.category.find_by_id(_data["category"]).id
        if len(_data["authors"]) > 0:
            movie.authors = self.rm.author.find_by_ids(_data["authors"])
        self.rm.movie.save(movie)

    def edit(self, form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        movie = self.rm.movie.find_by_id(id)
        movie_in = MoviePatchBody(**_data)
        movie.update(movie_in.dict())
        if _data["preview"] is not None:
            preview = self.rm.movie_preview.find_by_id(_data["preview"])
            if movie.preview is not None:
                movie.preview = None
                self.rm.save(movie)
            preview.movie_id = movie.id
        else:
            movie.preview = None
        if _data["category"] is not None:
            movie.category_id = self.rm.category.find_by_id(_data["category"]).id
        else:
            movie.category = None
        movie.authors = self.rm.author.find_by_ids(_data["authors"])
        self.rm.movie.save(movie)
