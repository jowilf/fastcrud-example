from typing import Optional

from common.admin import (HasMany, HasOne, ImageField, NumberField,
                          StringField, TextField)
from pydantic import ValidationError
from starlette.datastructures import FormData

from app.dependencies import repository_manager_ctx
from app.internal.base_models import BaseAdminModel
from app.models.category import Category, CategoryIn, CategoryPatchBody
from app.utils import pydantic_error_to_form_validation_error


class CategoryAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
    name = StringField(required=True)
    description = TextField()
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

    def find_by_pk(self, id) -> Optional[Category]:
        with repository_manager_ctx() as rm:
            return rm.category.find_by_id(id, False)

    def find_by_pks(self, ids) -> Optional[Category]:
        with repository_manager_ctx() as rm:
            return rm.category.find_by_ids(ids)

    def create(self, form_data: FormData):
        with repository_manager_ctx() as rm:
            try:
                _data = self._extract_fields(form_data)
                category_in = CategoryIn(**_data)
                category = rm.category.create(Category(**category_in.dict()))
                if _data["parent"] is not None:
                    category.parent_id = rm.category.find_by_id(_data["parent"]).id
                if len(_data["movies"]) > 0:
                    category.movies = rm.movie.find_by_ids(_data["movies"])
                if len(_data["childs"]) > 0:
                    category.childs = rm.category.find_by_ids(_data["childs"])
                return rm.category.save(category)
            except ValidationError as exc:
                raise pydantic_error_to_form_validation_error(exc)

    def edit(self, form_data: FormData, id):
        with repository_manager_ctx() as rm:
            try:
                _data = self._extract_fields(form_data, True)
                if _data["_keep_old_image"]:
                    _data.pop("image", None)
                category = rm.category.find_by_id(id)
                category_in = CategoryPatchBody(**_data)
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
