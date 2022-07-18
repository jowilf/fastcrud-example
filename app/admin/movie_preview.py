from typing import Optional

from common.admin import HasOne, ImageField, NumberField, StringField
from pydantic import ValidationError
from starlette.datastructures import FormData

from app.dependencies import repository_manager_ctx
from app.internal.base_models import BaseAdminModel
from app.models.movie_preview import (MoviePreview, MoviePreviewIn,
                                      MoviePreviewPatchBody)
from app.utils import pydantic_error_to_form_validation_error


class MoviePreviewAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
    images = ImageField(is_array=True)
    tags = StringField(is_array=True)
    movie = HasOne(identity="movie")

    def get_name(self) -> str:
        return "MoviePreview"

    def identity(self) -> str:
        return "movie_preview"

    def datasource(self) -> str:
        return "movie_previews:list"

    def find_by_pk(self, id) -> Optional[MoviePreview]:
        with repository_manager_ctx() as rm:
            return rm.movie_preview.find_by_id(id, False)

    def find_by_pks(self, ids) -> Optional[MoviePreview]:
        with repository_manager_ctx() as rm:
            return rm.movie_preview.find_by_ids(ids)

    def create(self, form_data: FormData):
        with repository_manager_ctx() as rm:
            try:
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
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)

    def edit(self, form_data: FormData, id):
        with repository_manager_ctx() as rm:
            try:
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
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)
