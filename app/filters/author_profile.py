from typing import List, Optional, Set, Union

from common.filters import BooleanFilter, HasFilter, NumberFilter
from fastapi import Query
from pydantic import Field

from app.internal.filters import BaseModelFilter, OrderBy
from app.models.author_profile import AuthorProfile


class AuthorProfileOrderBy(OrderBy):
    __cls__ = AuthorProfile

    def __init__(self, order_by: Optional[Set[str]] = Query(None)):
        self.values = order_by


class AuthorProfileFilter(BaseModelFilter):
    __cls__ = AuthorProfile

    id: Union[None, NumberFilter, int]
    protected: Union[None, BooleanFilter, bool]
    author: Optional["HasAuthorFilter"]
    or_: Optional[List["AuthorProfileFilter"]] = Field(None, alias="or")
    and_: Optional[List["AuthorProfileFilter"]] = Field(None, alias="and")
    not_: Optional["AuthorProfileFilter"] = Field(None, alias="not")


class HasAuthorProfileFilter(HasFilter, AuthorProfileFilter):
    pass


from app.filters.author import HasAuthorFilter

AuthorProfileFilter.update_forward_refs()
HasAuthorProfileFilter.update_forward_refs()
