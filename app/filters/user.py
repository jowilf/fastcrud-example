from datetime import datetime
from typing import List, Optional, Set, Union

from common.filters import DateTimeFilter, NumberFilter, StringFilter
from common.types import PhoneNumber
from fastapi import Query
from pydantic import EmailStr, Field

from app.internal.filters import BaseModelFilter, OrderBy
from app.models.user import User


class UserOrderBy(OrderBy):
    __cls__ = User

    def __init__(self, order_by: Optional[Set[str]] = Query(None)):
        self.values = order_by


class UserFilter(BaseModelFilter):
    __cls__ = User

    id: Union[None, NumberFilter, int]
    username: Union[None, StringFilter, str]
    phonenumber: Union[None, StringFilter, PhoneNumber]
    email: Union[None, StringFilter, EmailStr]
    password: Union[None, StringFilter, str]
    date_joined: Union[None, DateTimeFilter, datetime]
    or_: Optional[List["UserFilter"]] = Field(None, alias="or")
    and_: Optional[List["UserFilter"]] = Field(None, alias="and")
    not_: Optional["UserFilter"] = Field(None, alias="not")


UserFilter.update_forward_refs()
