from typing import TYPE_CHECKING, Optional

from common.admin import HasOne, ImageField, StringField
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models.movie_preview import (MoviePreview, MoviePreviewIn,
                                      MoviePreviewPatchBody)

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class MoviePreviewAdmin(BaseAdminModel):
    images = ImageField(is_array=True)
    tags = StringField(is_array=True)
    movie = HasOne(identity="movie")

    def get_name(self) -> str:
        return "MoviePreview"

    def identity(self) -> str:
        return "movie_preview"

    def datasource(self) -> str:
        return "api:movie_previews"

    def find_by_id(self, rm: "RepositoryManager", id) -> Optional[MoviePreview]:
        return rm.movie_preview.find_by_id(id, False)

    def create(self, rm: "RepositoryManager", form_data: FormData):
        _data = self._extract_fields(form_data)
        movie_preview_in = MoviePreviewIn(**_data)
        movie_preview = MoviePreview(**movie_preview_in.dict())
        if _data["movie"] is not None:
            movie = rm.movie.find_by_id(_data["movie"])
            if movie.preview is not None:
                movie.preview = None
                rm.save(movie)
            movie_preview.movie_id = movie.id
        rm.movie_preview.save(movie_preview)

    def edit(self, rm: "RepositoryManager", form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        if _data["_keep_old_images"]:
            _data.pop("images", None)
        movie_preview = rm.movie_preview.find_by_id(id)
        movie_preview_in = MoviePreviewPatchBody(**_data)
        movie_preview.update(movie_preview_in.dict())
        if _data["movie"] is not None:
            movie = rm.movie.find_by_id(_data["movie"])
            if movie.preview is not None:
                movie.preview = None
                rm.save(movie)
            movie_preview.movie_id = movie.id
        else:
            movie_preview.movie = None
        rm.movie_preview.save(movie_preview)
