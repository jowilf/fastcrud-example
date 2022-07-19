from enum import Enum
from typing import Any, List, Optional, Type
from pydantic import BaseModel


class BaseField(BaseModel):
    type: Optional[str] = "string"
    format: Optional[str] = None
    required: Optional[bool] = False
    is_array: Optional[bool] = False
    exclude_from_view: Optional[bool] = False
    exclude_from_list: Optional[bool] = False
    exclude_from_create: Optional[bool] = False
    exclude_from_edit: Optional[bool] = False


class NumberField(BaseField):
    type: str = "num"


class BooleanField(BaseField):
    type: str = "bool"


class StringField(BaseField):
    type: str = "string"


class TextField(StringField):
    multiline: bool = True


class EmailField(StringField):
    format: str = "email"


class PhoneField(StringField):
    format: str = "phone"


class EnumField(StringField):
    enum: bool = True
    values: List[Any] = []

    def __init__(self, type: Type[Enum], **data):
        values = list(map(lambda e: e.value, type))
        super().__init__(values=values, **data)


class DateTimeField(BaseField):
    type: str = "datetime"
    input_format: Optional[str] = None
    output_format: str = "MMMM Do, YYYY HH:mm:ss"
    api_format: Optional[str] = None


class DateField(BaseField):
    type: str = "date"
    input_format: Optional[str] = "YYYY-MM-DD"
    output_format: str = "MMMM Do, YYYY"
    api_format: Optional[str] = "YYYY-MM-DD"


class TimeField(BaseField):
    type: str = "time"
    input_format: Optional[str] = "HH:mm:ss"
    output_format: str = "HH:mm:ss"
    api_format: Optional[str] = "HH:mm:ss"


class JSONField(BaseField):
    type: str = "json"


class FileField(BaseField):
    type: str = "file"


class ImageField(FileField):
    type: str = "image"


class PasswordField(StringField):
    type: str = "password"
    exclude_from_view: bool = True
    exclude_from_list: bool = True
    exclude_from_edit: bool = True
    min_length: int = 8
    max_length: int = 20
    has_uppercase: bool = True
    has_lowercase: bool = True
    min_digits: int = 1
    allow_spaces: bool = False
    special_chars: str = "&%$()=!?*+-.,:;"


class RelationField(BaseField):
    type: str = "relation"
    identity: str


class HasOne(RelationField):
    pass


class HasMany(RelationField):
    many: bool = True
    is_array: Optional[bool] = True
