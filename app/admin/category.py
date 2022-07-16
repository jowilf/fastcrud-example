from typing import TYPE_CHECKING, Optional

from common.admin import (HasMany, HasOne, ImageField, NumberField,
                          StringField, TextField)
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models.category import Category, CategoryIn, CategoryPatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


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

    def __init__(self, rm: "RepositoryManager" = None):
        self.rm = rm

    def get_name(self) -> str:
        return "Category"

    def identity(self) -> str:
        return "category"

    def datasource(self) -> str:
        return "api:categories"

    def find_by_pk(self, id) -> Optional[Category]:
        return self.rm.category.find_by_id(id, False)

    def create(self, form_data: FormData):
        _data = self._extract_fields(form_data)
        category_in = CategoryIn(**_data)
        category = Category(**category_in.dict())
        if _data["parent"] is not None:
            category.parent_id = self.rm.category.find_by_id(_data["parent"]).id
        if len(_data["movies"]) > 0:
            category.movies = self.rm.movie.find_by_ids(_data["movies"])
        if len(_data["childs"]) > 0:
            category.childs = self.rm.category.find_by_ids(_data["childs"])
        self.rm.category.save(category)

    def edit(self, form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        if _data["_keep_old_image"]:
            _data.pop("image", None)
        category = self.rm.category.find_by_id(id)
        category_in = CategoryPatchBody(**_data)
        category.update(category_in.dict())
        if _data["parent"] is not None:
            category.parent_id = self.rm.category.find_by_id(_data["parent"]).id
        else:
            category.parent = None
        category.movies = self.rm.movie.find_by_ids(_data["movies"])
        category.childs = self.rm.category.find_by_ids(_data["childs"])
        self.rm.category.save(category)
