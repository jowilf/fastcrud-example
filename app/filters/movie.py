from datetime import date, datetime
from typing import List, Optional, Set, Union

from common.filters import (AnyFilter, DateFilter, DateTimeFilter, HasFilter,
                            NumberFilter, StringFilter)
from fastapi import Query
from pydantic import Field

from app.internal.filters import BaseModelFilter, OrderBy
from app.models.movie import Movie


class MovieOrderBy(OrderBy):
    __cls__ = Movie

    def __init__(self, order_by: Optional[Set[str]] = Query(None)):
        self.values = order_by


class MovieFilter(BaseModelFilter):
    __cls__ = Movie

    id: Union[None, NumberFilter, int]
    name: Union[None, StringFilter, str]
    description: Union[None, StringFilter, str]
    watch_count: Union[None, NumberFilter, int]
    release_date: Union[None, DateFilter, date]
    created_at: Union[None, DateTimeFilter, datetime]
    updated_at: Union[None, DateTimeFilter, datetime]
    preview: Optional["HasMoviePreviewFilter"]
    category: Optional["HasCategoryFilter"]
    authors: Optional["AnyAuthorFilter"]
    or_: Optional[List["MovieFilter"]] = Field(None, alias="or")
    and_: Optional[List["MovieFilter"]] = Field(None, alias="and")
    not_: Optional["MovieFilter"] = Field(None, alias="not")


class HasMovieFilter(HasFilter, MovieFilter):
    pass


class AnyMovieFilter(AnyFilter, MovieFilter):
    pass


from app.filters.author import AnyAuthorFilter
from app.filters.category import HasCategoryFilter
from app.filters.movie_preview import HasMoviePreviewFilter

MovieFilter.update_forward_refs()
HasMovieFilter.update_forward_refs()
AnyMovieFilter.update_forward_refs()
