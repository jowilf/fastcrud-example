from typing import Any, Dict, Optional

from common.types import FileField, FileInfo
from fastapi import File, Form, UploadFile
from pydantic import Json
from sqlmodel import BOOLEAN, JSON, Column, Field, Relationship, SQLModel

from app.internal.base_models import BaseSQLModel
from app.utils import _AllOptionalMeta as AllOptional


class AuthorProfileBase(SQLModel):
    info: Optional[Dict[Any, Any]] = Field(None, sa_column=Column(JSON))
    protected: bool = Field(..., sa_column=Column(BOOLEAN, nullable=False, index=True))


class AuthorProfileRelationFields(SQLModel):
    pass


class AuthorProfile(
    AuthorProfileRelationFields, AuthorProfileBase, BaseSQLModel, table=True
):
    __tablename__ = "author_profile"
    file: FileInfo = Field(
        ..., sa_column=Column(FileField(upload_storage="default"), nullable=False)
    )
    author: Optional["Author"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Author.profile_id", uselist=False),
        back_populates="profile",
    )


class AuthorProfileInBase(AuthorProfileBase):
    file: FileInfo

    def dict(self):
        v = super().dict()
        v.update(file=self.file)
        return v


class AuthorProfileIn(AuthorProfileRelationFields, AuthorProfileInBase):
    pass


def author_profile_in_form(
    file: UploadFile = File(...),
    info: Optional[Json[Dict[Any, Any]]] = Form(None),
    protected: bool = Form(...),
):
    return AuthorProfileIn(file=FileInfo(content=file), info=info, protected=protected)


class AuthorProfilePatchBody(
    AuthorProfileRelationFields, AuthorProfileBase, metaclass=AllOptional
):
    pass


class AuthorProfileRelationsOut(BaseSQLModel):
    author: Optional["AuthorOutWithoutRelations"]


class AuthorProfileOutWithoutRelations(AuthorProfileBase, BaseSQLModel):
    file: FileInfo


class AuthorProfileOut(
    AuthorProfileRelationsOut, AuthorProfileOutWithoutRelations, metaclass=AllOptional
):
    pass


from app.models.author import Author, AuthorOutWithoutRelations

AuthorProfileOut.update_forward_refs()
