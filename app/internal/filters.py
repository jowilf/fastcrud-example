from typing import Type

from common.filters.sqlalchemy import SQLAlchemyModelFilter
from fastapi import HTTPException, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from querystring_parser import parser
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


class PaginationQuery:
    def __init__(self, skip: int = Query(0), limit: int = Query(100)):
        self.skip = skip
        self.limit = limit


class OrderBy:
    __cls__ = None

    def order_list(self):
        if self.values is None:
            return [None]
        _list = []
        for value in self.values:
            attr, order = None, "asc"
            value = value.strip().split(maxsplit=1)
            if len(value) == 1:
                attr = getattr(self.__cls__, value[0], None)
            else:
                attr, order = getattr(self.__cls__, value[0], None), value[1]
            if attr is not None:
                _list.append(attr.desc() if order.lower() == "desc" else attr)
        return _list


class BaseModelFilter(SQLAlchemyModelFilter):
    __cls__ = None

    @classmethod
    def from_query(cls: Type["BaseModelFilter"], request: Request):
        try:
            if "where" in request.query_params.keys():
                return cls.parse_raw(request.query_params.get("where"))
            else:
                filter = parser.parse("%s" % request.query_params, normalized=True).get(
                    "where"
                )
                if filter is not None:
                    return cls(**filter)
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors)
        except BaseException as e:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, "Invalid where filter")
        return None
