from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

from common.admin import AdminModel, NumberField
from common.types import FileInfo
from sqlalchemy import MetaData
from sqlmodel import Field, SQLModel
from starlette.datastructures import FormData, UploadFile

if TYPE_CHECKING:
    from .repository_manager import RepositoryManager


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
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )

    def pk(self) -> str:
        return "id"

    @abstractmethod
    def find_by_id(self, rm: "RepositoryManager", id):
        pass

    @abstractmethod
    def create(self, rm: "RepositoryManager", form_data: FormData):
        pass

    @abstractmethod
    def edit(self, rm: "RepositoryManager", form_data: FormData, id):
        pass

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
