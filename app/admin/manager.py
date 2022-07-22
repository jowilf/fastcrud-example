from typing import TYPE_CHECKING, Optional

from pydantic import ValidationError
from sf_admin import HasMany, NumberField, TextField
from starlette.datastructures import FormData
from starlette.requests import Request

from app.internal.base_models import BaseAdminModel
from app.models.manager import Manager, ManagerIn, ManagerPatchBody
from app.utils import pydantic_error_to_form_validation_error

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class ManagerAdmin(BaseAdminModel):
    id = NumberField(exclude_from_create=True, exclude_from_edit=True)
    lastname = TextField(required=True)
    firstname = TextField(required=True)
    authors = HasMany(identity="author")

    def get_name(self) -> str:
        return "Manager"

    def identity(self) -> str:
        return "manager"

    def datasource(self) -> str:
        return "managers:list"

    def find_by_pk(self, request: Request, id) -> Optional[Manager]:
        rm: RepositoryManager = request.state.rm
        return rm.manager.find_by_id(id, False)

    def find_by_pks(self, request: Request, ids) -> Optional[Manager]:
        rm: RepositoryManager = request.state.rm
        return rm.manager.find_by_ids(ids)

    def create(self, request: Request, form_data: FormData):
        rm: RepositoryManager = request.state.rm
        try:
            _data = self._extract_fields(form_data)
            manager_in = ManagerIn(**_data)
            manager = rm.manager.create(manager_in)
            if len(_data["authors"]) > 0:
                manager.authors = rm.author.find_by_ids(_data["authors"])
            return rm.manager.save(manager)
        except ValidationError as exc:
            raise pydantic_error_to_form_validation_error(exc)

    def edit(self, request: Request, form_data: FormData, id):
        rm: RepositoryManager = request.state.rm
        try:
            _data = self._extract_fields(form_data, True)
            manager = rm.manager.find_by_id(id)
            manager_in = ManagerPatchBody(**_data)
            manager.update(manager_in.dict())
            manager.authors = rm.author.find_by_ids(_data["authors"])
            return rm.manager.save(manager)
        except ValidationError as exc:
            raise pydantic_error_to_form_validation_error(exc)
