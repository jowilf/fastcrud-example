from abc import abstractmethod
import inspect
import json
from typing import Any, Dict, List, Tuple
from fastapi import Request

from loguru import logger

from common.admin.helpers import slugify_class_name
from common.admin.fields import (
    BaseField,
    DateTimeField,
    FileField,
    HasMany,
    ImageField,
    PhoneField,
    RelationField,
    StringField,
    BooleanField,
    TextField,
    EmailField,
    EnumField,
    DateField,
    TimeField,
    JSONField,
    NumberField,
)

from pydantic import BaseModel, EmailStr
from fastapi.datastructures import FormData


class AdminModel:
    def identity(self) -> str:
        return slugify_class_name(self.__class__.__name__)

    @abstractmethod
    def get_name(self) -> str:
        raise NotImplemented

    @abstractmethod
    def pk(self) -> str:
        pass

    @abstractmethod
    def datasource(self) -> str:
        pass

    @abstractmethod
    def find_by_pk(self, id):
        pass

    @abstractmethod
    def create(self, form_data: FormData):
        pass

    @abstractmethod
    def edit(self, form_data: FormData, id):
        pass

    def can_view(self, request: Request) -> bool:
        pass

    def can_edit(self, request: Request) -> bool:
        pass

    def can_create(self, request: Request) -> bool:
        pass

    def _export_columns(self) -> List[int]:
        return list(
            range(
                2,
                2
                + len(
                    list(
                        filter(
                            lambda f: not f[1].exclude_from_list,
                            self.all_fields(),
                        )
                    )
                ),
            )
        )

    def search_columns(self) -> List[int]:
        columns, i = dict(), 0
        for name, field in self.all_fields():
            if (
                type(field)
                in [
                    DateTimeField,
                    PhoneField,
                    StringField,
                    BooleanField,
                    TextField,
                    EmailField,
                    EnumField,
                    DateField,
                    TimeField,
                    JSONField,
                    NumberField,
                ]
                and not field.is_array
            ):
                columns[i + 2] = name
            if not field.exclude_from_list:
                i += 1

        return columns

    def all_fields(self) -> List[Tuple[str, BaseField]]:
        fields = []
        for attr in type(self).__dict__:
            value = getattr(self, attr)
            if isinstance(value, BaseField):
                fields.append((attr, value))
        return fields

    def dict(self) -> dict:
        d = {}
        for name, field in self.all_fields():
            d[name] = field.dict()
        return d

    def _extract_fields(
        self, form_data: FormData, is_edit: bool = False
    ) -> Dict[str, Any]:
        data = dict()
        for name, field in self.all_fields():
            if (is_edit and not field.exclude_from_edit) or (
                not is_edit and not field.exclude_from_create
            ):
                if (
                    type(field) in [NumberField, EmailField, PhoneField]
                    and form_data.get(name) == ""
                ):
                    data[name] = None
                elif type(field) == JSONField:
                    data[name] = json.loads(form_data.get(name))
                elif field.is_array:
                    data[name] = form_data.getlist(name)
                else:
                    data[name] = form_data.get(name)
                if type(field) in [FileField, ImageField]:
                    data[f"_keep_old_{name}"] = form_data.get(
                        f"_keep_old_{name}"
                    )
        logger.info(data)
        return data
