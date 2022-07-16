from typing import Generic, List, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class CountResponse(BaseModel):
    count: int


class PaginatedData(GenericModel, Generic[T]):
    items: List[T]
    total: int
