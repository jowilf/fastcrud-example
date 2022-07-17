from typing import TYPE_CHECKING, Optional

from common.admin import HasMany, NumberField, TextField
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models.manager import Manager, ManagerIn, ManagerPatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class ManagerAdmin(BaseAdminModel):
    id = NumberField(
        exclude_from_create=True, exclude_from_edit=True, exclude_from_view=True
    )
    lastname = TextField(required=True)
    firstname = TextField(required=True)
    authors = HasMany(identity="author")

    def __init__(self, rm: "RepositoryManager" = None):
        self.rm = rm

    def get_name(self) -> str:
        return "Manager"

    def identity(self) -> str:
        return "manager"

    def datasource(self) -> str:
        return "managers:list"

    def find_by_pk(self, id) -> Optional[Manager]:
        return self.rm.manager.find_by_id(id, False)

    def create(self, form_data: FormData):
        _data = self._extract_fields(form_data)
        manager_in = ManagerIn(**_data)
        manager = Manager(**manager_in.dict())
        if len(_data["authors"]) > 0:
            manager.authors = self.rm.author.find_by_ids(_data["authors"])
        self.rm.manager.save(manager)

    def edit(self, form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        manager = self.rm.manager.find_by_id(id)
        manager_in = ManagerPatchBody(**_data)
        manager.update(manager_in.dict())
        manager.authors = self.rm.author.find_by_ids(_data["authors"])
        self.rm.manager.save(manager)
