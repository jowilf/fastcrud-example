from typing import List, Optional, Set, Union

from common.filters import AnyFilter, HasFilter, NumberFilter, StringFilter
from fastapi import Query
from pydantic import Field

from app.internal.filters import BaseModelFilter, OrderBy
from app.models.category import Category


class CategoryOrderBy(OrderBy):
    __cls__ = Category

    def __init__(self, order_by: Optional[Set[str]] = Query(None)):
        self.values = order_by


class CategoryFilter(BaseModelFilter):
    __cls__ = Category

    id: Union[None, NumberFilter, int]
    name: Union[None, StringFilter, str]
    description: Union[None, StringFilter, str]
    parent: Optional["HasCategoryFilter"]
    movies: Optional["AnyMovieFilter"]
    childs: Optional["AnyCategoryFilter"]
    or_: Optional[List["CategoryFilter"]] = Field(None, alias="or")
    and_: Optional[List["CategoryFilter"]] = Field(None, alias="and")
    not_: Optional["CategoryFilter"] = Field(None, alias="not")


class HasCategoryFilter(HasFilter, CategoryFilter):
    pass


class AnyCategoryFilter(AnyFilter, CategoryFilter):
    pass


from app.filters.movie import AnyMovieFilter

CategoryFilter.update_forward_refs()
HasCategoryFilter.update_forward_refs()
AnyCategoryFilter.update_forward_refs()
