from typing import List, Optional, Set, Union

from common.filters import HasFilter, NumberFilter, StringFilter
from fastapi import Query
from pydantic import Field

from app.internal.filters import BaseModelFilter, OrderBy
from app.models.manager import Manager


class ManagerOrderBy(OrderBy):
    __cls__ = Manager

    def __init__(self, order_by: Optional[Set[str]] = Query(None)):
        self.values = order_by


class ManagerFilter(BaseModelFilter):
    __cls__ = Manager

    id: Union[None, NumberFilter, int]
    lastname: Union[None, StringFilter, str]
    firstname: Union[None, StringFilter, str]
    authors: Optional["AnyAuthorFilter"]
    or_: Optional[List["ManagerFilter"]] = Field(None, alias="or")
    and_: Optional[List["ManagerFilter"]] = Field(None, alias="and")
    not_: Optional["ManagerFilter"] = Field(None, alias="not")


class HasManagerFilter(HasFilter, ManagerFilter):
    pass


from app.filters.author import AnyAuthorFilter

ManagerFilter.update_forward_refs()
HasManagerFilter.update_forward_refs()
