from typing import List

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel

from app.internal.base_models import BaseSQLModel
from app.utils import _AllOptionalMeta as AllOptional


class ManagerBase(SQLModel):
    lastname: str = Field(
        ..., sa_column=Column(VARCHAR(255), nullable=False, index=True)
    )
    firstname: str = Field(
        ..., sa_column=Column(VARCHAR(255), nullable=False, index=True)
    )


class ManagerRelationFields(SQLModel):
    pass


class Manager(ManagerRelationFields, ManagerBase, BaseSQLModel, table=True):
    __tablename__ = "manager"
    authors: List["Author"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Author.manager_id"),
        back_populates="manager",
    )


class ManagerInBase(ManagerBase):
    pass


class ManagerIn(ManagerRelationFields, ManagerInBase):
    pass


class ManagerPatchBody(ManagerIn, metaclass=AllOptional):
    pass


class ManagerRelationsOut(SQLModel):
    authors: List["AuthorOutWithoutRelations"]


class ManagerOutWithoutRelations(ManagerBase, BaseSQLModel):
    pass


class ManagerOut(
    ManagerRelationsOut, ManagerOutWithoutRelations, metaclass=AllOptional
):
    pass


from app.models.author import Author, AuthorOutWithoutRelations

ManagerOut.update_forward_refs()
