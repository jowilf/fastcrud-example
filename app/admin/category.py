from typing import TYPE_CHECKING, Optional

from common.admin import (HasMany, HasOne, ImageField, NumberField,
                          TextAreaField, TextField)
from pydantic import ValidationError
from starlette.datastructures import FormData
from starlette.requests import Request

from app.internal.base_models import BaseAdminModel
from app.models.category import Category, CategoryIn, CategoryPatchBody
from app.utils import pydantic_error_to_form_validation_error

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class CategoryAdmin(BaseAdminModel):
    id = NumberField(exclude_from_create=True, exclude_from_edit=True)
    name = TextField(required=True)
    description = TextAreaField()
    image = ImageField()
    parent = HasOne(identity="category")
    movies = HasMany(identity="movie")
    childs = HasMany(identity="category")

    def get_name(self) -> str:
        return "Category"

    def identity(self) -> str:
        return "category"

    def datasource(self) -> str:
        return "categories:list"

    def find_by_pk(self, request: Request, id) -> Optional[Category]:
        rm: RepositoryManager = request.state.rm
        return rm.category.find_by_id(id, False)

    def find_by_pks(self, request: Request, ids) -> Optional[Category]:
        rm: RepositoryManager = request.state.rm
        return rm.category.find_by_ids(ids)

    def create(self, request: Request, form_data: FormData):
        rm: RepositoryManager = request.state.rm
        try:
            _data = self._extract_fields(form_data)
            category_in = CategoryIn(**_data)
            category = rm.category.create(category_in)
            if _data["parent"] is not None:
                category.parent_id = rm.category.find_by_id(_data["parent"]).id
            if len(_data["movies"]) > 0:
                category.movies = rm.movie.find_by_ids(_data["movies"])
            if len(_data["childs"]) > 0:
                category.childs = rm.category.find_by_ids(_data["childs"])
            return rm.category.save(category)
        except ValidationError as exc:
            raise pydantic_error_to_form_validation_error(exc)

    def edit(self, request: Request, form_data: FormData, id):
        rm: RepositoryManager = request.state.rm
        try:
            _data = self._extract_fields(form_data, True)
            category = rm.category.find_by_id(id)
            category_in = CategoryPatchBody(**_data)
            if not _data["_keep_old_image"]:
                category.image = _data["image"]
            category.update(category_in.dict())
            if _data["parent"] is not None:
                category.parent_id = rm.category.find_by_id(_data["parent"]).id
            else:
                category.parent = None
            category.movies = rm.movie.find_by_ids(_data["movies"])
            category.childs = rm.category.find_by_ids(_data["childs"])
            return rm.category.save(category)
        except ValidationError as exc:
            raise pydantic_error_to_form_validation_error(exc)
