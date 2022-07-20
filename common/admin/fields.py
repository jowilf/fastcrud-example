from enum import Enum
from typing import Any, List, Optional, Type
from pydantic import BaseModel


class BaseField(BaseModel):
    type: Optional[str] = None
    search_builder_type: Optional[str] = None
    format: Optional[str] = None
    required: Optional[bool] = False
    is_array: Optional[bool] = False
    exclude_from_view: Optional[bool] = False
    exclude_from_list: Optional[bool] = False
    exclude_from_create: Optional[bool] = False
    exclude_from_edit: Optional[bool] = False
    searchable: Optional[bool] = False


class BooleanField(BaseField):
    type: str = "bool"
    search_builder_type: Optional[str] = "bool"
    searchable: Optional[bool] = True


class NumberField(BaseField):
    type: str = "num"
    search_builder_type: str = "num"
    searchable: Optional[bool] = True


class TextField(BaseField):
    type: Optional[str] = "text"
    input_type = "text"
    search_builder_type: Optional[str] = "string"
    searchable: Optional[bool] = True


class TextAreaField(TextField):
    multiline: bool = True


class TagsField(TextField):
    type: Optional[str] = "tags"
    searchable: Optional[bool] = False
    is_array: Optional[bool] = True


class EmailField(TextField):
    input_type = "email"
    searchable: Optional[bool] = True


class PhoneField(TextField):
    input_type = "phone"
    searchable: Optional[bool] = True


class EnumField(BaseField):
    type = "enum"
    search_builder_type: Optional[str] = "string"
    values: List[Any] = []
    searchable: Optional[bool] = True

    def __init__(self, type: Type[Enum], **data):
        values = list(map(lambda e: e.value, type))
        super().__init__(values=values, **data)


class DateTimeField(BaseField):
    type: str = "datetime"
    input_format: Optional[str] = None
    output_format: str = "MMMM D, YYYY HH:mm:ss"
    api_format: Optional[str] = None
    search_builder_type: Optional[str] = "moment-MMMM D, YYYY HH:mm:ss"
    python_output_format: Optional[str] = "%B %d, %Y %H:%M:%S"
    searchable: Optional[bool] = True


class DateField(BaseField):
    type: str = "date"
    input_format: Optional[str] = "YYYY-MM-DD"
    output_format: str = "MMMM D, YYYY"
    api_format: Optional[str] = "YYYY-MM-DD"
    search_builder_type: Optional[str] = "moment-MMMM D, YYYY"
    python_output_format: Optional[str] = "%B %d, %Y"
    searchable: Optional[bool] = True


class TimeField(BaseField):
    type: str = "time"
    input_format: Optional[str] = "HH:mm:ss"
    output_format: str = "HH:mm:ss"
    api_format: Optional[str] = "HH:mm:ss"
    search_builder_type: Optional[str] = "moment-HH:mm:ss"
    python_output_format: Optional[str] = "%H:%M:%S"
    searchable: Optional[bool] = True


class JSONField(BaseField):
    type: str = "json"


class FileField(BaseField):
    type: str = "file"


class ImageField(FileField):
    type: str = "image"


class PasswordField(TextField):
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
