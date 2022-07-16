from typing import TYPE_CHECKING, Optional

from common.admin import HasMany, TextField
from starlette.datastructures import FormData

from app.internal.base_models import BaseAdminModel
from app.models.manager import Manager, ManagerIn, ManagerPatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class ManagerAdmin(BaseAdminModel):
    lastname = TextField(required=True)
    firstname = TextField(required=True)
    authors = HasMany(identity="author")

    def get_name(self) -> str:
        return "Manager"

    def identity(self) -> str:
        return "manager"

    def datasource(self) -> str:
        return "api:managers"

    def find_by_id(self, rm: "RepositoryManager", id) -> Optional[Manager]:
        return rm.manager.find_by_id(id, False)

    def create(self, rm: "RepositoryManager", form_data: FormData):
        _data = self._extract_fields(form_data)
        manager_in = ManagerIn(**_data)
        manager = Manager(**manager_in.dict())
        if len(_data["authors"]) > 0:
            manager.authors = rm.author.find_by_ids(_data["authors"])
        rm.manager.save(manager)

    def edit(self, rm: "RepositoryManager", form_data: FormData, id):
        _data = self._extract_fields(form_data, True)
        manager = rm.manager.find_by_id(id)
        manager_in = ManagerPatchBody(**_data)
        manager.update(manager_in.dict())
        manager.authors = rm.author.find_by_ids(_data["authors"])
        rm.manager.save(manager)
