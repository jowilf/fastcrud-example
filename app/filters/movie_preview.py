from typing import List, Optional, Set, Union

from common.filters import HasFilter, NumberFilter
from fastapi import Query
from pydantic import Field

from app.internal.filters import BaseModelFilter, OrderBy
from app.models.movie_preview import MoviePreview


class MoviePreviewOrderBy(OrderBy):
    __cls__ = MoviePreview

    def __init__(self, order_by: Optional[Set[str]] = Query(None)):
        self.values = order_by


class MoviePreviewFilter(BaseModelFilter):
    __cls__ = MoviePreview

    id: Union[None, NumberFilter, int]
    movie: Optional["HasMovieFilter"]
    or_: Optional[List["MoviePreviewFilter"]] = Field(None, alias="or")
    and_: Optional[List["MoviePreviewFilter"]] = Field(None, alias="and")
    not_: Optional["MoviePreviewFilter"] = Field(None, alias="not")


class HasMoviePreviewFilter(HasFilter, MoviePreviewFilter):
    pass


from app.filters.movie import HasMovieFilter

MoviePreviewFilter.update_forward_refs()
HasMoviePreviewFilter.update_forward_refs()
