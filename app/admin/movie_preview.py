from typing import TYPE_CHECKING, Optional

from common.admin import HasOne, ImageField, NumberField, StringField
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models.movie_preview import (MoviePreview, MoviePreviewIn,
                                      MoviePreviewPatchBody)

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class MoviePreviewAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
    images = ImageField(is_array=True)
    tags = StringField(is_array=True)
    movie = HasOne(identity="movie")

    def __init__(self, rm: "RepositoryManager" = None):
        self.rm = rm

    def get_name(self) -> str:
        return "MoviePreview"

    def identity(self) -> str:
        return "movie_preview"

    def datasource(self) -> str:
        return "movie_previews:list"

    def find_by_pk(self, id) -> Optional[MoviePreview]:
        return self.rm.movie_preview.find_by_id(id, False)

    def create(self, form_data: FormData):
        _data = self._extract_fields(form_data)
        movie_preview_in = MoviePreviewIn(**_data)
        movie_preview = MoviePreview(**movie_preview_in.dict())
        if _data["movie"] is not None:
            movie = self.rm.movie.find_by_id(_data["movie"])
            if movie.preview is not None:
                movie.preview = None
                self.rm.save(movie)
            movie_preview.movie_id = movie.id
        self.rm.movie_preview.save(movie_preview)

    def edit(self, form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        if _data["_keep_old_images"]:
            _data.pop("images", None)
        movie_preview = self.rm.movie_preview.find_by_id(id)
        movie_preview_in = MoviePreviewPatchBody(**_data)
        movie_preview.update(movie_preview_in.dict())
        if _data["movie"] is not None:
            movie = self.rm.movie.find_by_id(_data["movie"])
            if movie.preview is not None:
                movie.preview = None
                self.rm.save(movie)
            movie_preview.movie_id = movie.id
        else:
            movie_preview.movie = None
        self.rm.movie_preview.save(movie_preview)
