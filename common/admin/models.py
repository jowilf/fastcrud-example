from abc import abstractmethod
import inspect
import json
from typing import Any, Dict, List, Tuple
from fastapi import Request

from loguru import logger
from common.admin.exceptions import FormValidationError

from common.admin.helpers import slugify_class_name
from common.admin.fields import (
    BaseField,
    DateTimeField,
    FileField,
    HasMany,
    ImageField,
    PhoneField,
    RelationField,
    BooleanField,
    TagsField,
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
    def find_by_pk(self, request: Request, id):
        pass

    @abstractmethod
    def find_by_pks(self, request: Request, ids):
        pass

    @abstractmethod
    def create(self, request: Request, form_data: FormData):
        pass

    @abstractmethod
    def edit(self, request: Request, form_data: FormData, id):
        pass

    def can_view(self, request: Request) -> bool:
        return True

    def can_edit(self, request: Request) -> bool:
        return True

    def can_create(self, request: Request) -> bool:
        return True

    def can_delete(self, request: Request) -> bool:
        return True

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

    def search_columns(self) -> Dict[int, str]:
        columns, i = dict(), 0
        for name, field in self.all_fields():
            if (not field.is_array) and field.searchable:
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

    def cols(self) -> dict:
        d = {}
        for name, field in self.all_fields():
            d[name] = field.dict()
        return d

    def _extract_fields(
        self, form_data: FormData, is_edit: bool = False
    ) -> Dict[str, Any]:
        logger.info(form_data)
        data = dict()
        for name, field in self.all_fields():
            if (is_edit and not field.exclude_from_edit) or (
                not is_edit and not field.exclude_from_create
            ):
                if (
                    type(field)
                    in [
                        NumberField,
                        EmailField,
                        PhoneField,
                        DateTimeField,
                        DateField,
                        TimeField,
                    ]
                    and form_data.get(name) == ""
                ):
                    data[name] = None
                elif type(field) == BooleanField and form_data.get(name) is None:
                    data[name] = False
                elif type(field) == JSONField and form_data.get(name) is not None:
                    try:
                        data[name] = json.loads(form_data.get(name))
                    except:
                        raise FormValidationError({name: "Invalid JSON value"})
                elif field.is_array:
                    data[name] = form_data.getlist(name)
                else:
                    data[name] = form_data.get(name)
                if type(field) in [FileField, ImageField]:
                    data[f"_keep_old_{name}"] = form_data.get(f"_keep_old_{name}")
        logger.info(data)
        return data

    def item_to_dict(self, value) -> Dict[str, str]:
        data = dict()
        for name in self.search_columns().values():
            data[name] = str(getattr(value, name))
        return data

    def _select2_initial_data(self, request: Request, pk):
        items = []
        if type(pk) is list:
            items = self.find_by_pks(request, pk)
        else:
            items = [self.find_by_pk(request, pk)]
        datas = []
        for item in items:
            data = self.item_to_dict(item)
            data["selected"] = True
            datas.append(data)
        return datas

    def need_select2(self) -> bool:
        for name, field in self.all_fields():
            if (
                field.is_array
                or isinstance(field, EnumField)
                or isinstance(field, RelationField)
                or isinstance(field, TagsField)
            ):
                return True
        return False

    def need_jsoneditor(self) -> bool:
        for name, field in self.all_fields():
            if isinstance(field, JSONField):
                return True
        return False
