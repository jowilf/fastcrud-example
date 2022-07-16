from datetime import date, datetime, time
from typing import List, Optional, Set, Union

from common.filters import (AnyFilter, DateFilter, DateTimeFilter, HasFilter,
                            NumberFilter, StringFilter, TimeFilter)
from fastapi import Query
from pydantic import Field

from app.internal.filters import BaseModelFilter, OrderBy
from app.models.author import Author


class AuthorOrderBy(OrderBy):
    __cls__ = Author

    def __init__(self, order_by: Optional[Set[str]] = Query(None)):
        self.values = order_by


class AuthorFilter(BaseModelFilter):
    __cls__ = Author

    id: Union[None, NumberFilter, int]
    lastname: Union[None, StringFilter, str]
    firstname: Union[None, StringFilter, str]
    sex: Union[None, StringFilter, str]
    birthday: Union[None, DateFilter, date]
    wakeup_time: Union[None, TimeFilter, time]
    wakeup_day: Union[None, DateTimeFilter, datetime]
    created_at: Union[None, DateTimeFilter, datetime]
    updated_at: Union[None, DateTimeFilter, datetime]
    profile: Optional["HasAuthorProfileFilter"]
    manager: Optional["HasManagerFilter"]
    movies: Optional["AnyMovieFilter"]
    friends: Optional["AnyAuthorFilter"]
    friends_of: Optional["AnyAuthorFilter"]
    or_: Optional[List["AuthorFilter"]] = Field(None, alias="or")
    and_: Optional[List["AuthorFilter"]] = Field(None, alias="and")
    not_: Optional["AuthorFilter"] = Field(None, alias="not")


class HasAuthorFilter(HasFilter, AuthorFilter):
    pass


class AnyAuthorFilter(AnyFilter, AuthorFilter):
    pass


from app.filters.author_profile import HasAuthorProfileFilter
from app.filters.manager import HasManagerFilter
from app.filters.movie import AnyMovieFilter

AuthorFilter.update_forward_refs()
HasAuthorFilter.update_forward_refs()
AnyAuthorFilter.update_forward_refs()
