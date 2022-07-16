from typing import TYPE_CHECKING, Any, Dict, Optional

from common.admin import AdminModel
from common.types import FileInfo
from sqlalchemy import MetaData
from sqlmodel import Field, SQLModel
from starlette.datastructures import FormData, UploadFile

if TYPE_CHECKING:
    pass


class BaseTable(SQLModel):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class BaseSQLModel(BaseTable):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

    def update(self, new_values: dict):
        for key, value in new_values.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BaseAdminModel(AdminModel):
    def pk(self) -> str:
        return "id"

    def _extract_fields(
        self, form_data: FormData, is_edit: bool = False
    ) -> Dict[str, Any]:
        data = super()._extract_fields(form_data, is_edit)
        for key in data.keys():
            if isinstance(data[key], UploadFile):
                data[key] = FileInfo(content=data[key])
            elif (
                type(data[key]) is list
                and len(data[key]) > 0
                and all([isinstance(v, UploadFile) for v in data[key]])
            ):
                data[key] = [FileInfo(content=c) for c in data[key]]
        return data
