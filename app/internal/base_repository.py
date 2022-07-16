from typing import Generic, List, Optional, Type, TypeVar, Union

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY

from .base_models import BaseSQLModel
from .filters import BaseModelFilter, OrderBy, PaginationQuery
from .response import CountResponse

T = TypeVar("T", bound=BaseSQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, cls: Type[T], session: Session) -> None:
        self.session = session
        self.cls = cls

    def find_all(
        self,
        pagination: PaginationQuery = PaginationQuery(),
        where: Optional[BaseModelFilter] = None,
        order_by: Optional[OrderBy] = None,
        count=False,
    ) -> Union[List[T], int]:
        stmt = select(self.cls).offset(pagination.skip)
        if pagination.limit > 0:
            stmt = stmt.limit(pagination.limit)
        cnt_stmt = select(func.count()).select_from(self.cls)
        if where is not None:
            query = where.to_query()
            stmt = stmt.where(query)
            cnt_stmt = cnt_stmt.where(query)
        if order_by is not None:
            stmt = stmt.order_by(*order_by.order_list())
        if count:
            return self.session.exec(cnt_stmt).one()
        return self.session.exec(stmt).all()

    def find_one(self, where: Optional[BaseModelFilter]) -> Optional[T]:
        stmt = select(self.cls)
        if where is not None:
            stmt = stmt.where(where.to_query())
        return self.session.exec(stmt).one_or_none()

    def find_by_id(self, id: int, raise_exception=True) -> T:
        entity = self.session.get(self.cls, id)
        if entity is None and raise_exception:
            raise HTTPException(
                HTTP_404_NOT_FOUND, f"Can't find {self.cls.__name__} with id={id}"
            )
        return entity

    def find_by_ids(self, ids: List[int]) -> List[T]:
        stmt = select(self.cls).where(self.cls.id.in_(ids))
        entities = self.session.exec(stmt).all()
        if len(entities) != len(ids):
            not_found_ids = list(
                filter(lambda id: id not in [e.id for e in entities], ids)
            )
            raise HTTPException(
                HTTP_404_NOT_FOUND,
                f"{self.cls.__name__} with ids: {not_found_ids} not found",
            )
        return entities

    def save(self, instance: T) -> T:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, where: Optional[BaseModelFilter]) -> CountResponse:
        if where is None:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, "Invalid where filter")
        items = self.find_all(PaginationQuery(0, -1), where)
        for item in items:
            self.session.delete(item)
        self.session.commit()
        return CountResponse(count=len(items))
