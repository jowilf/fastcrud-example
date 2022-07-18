from typing import List, Optional

from common.types import FileField, FileInfo
from fastapi import File, Form, UploadFile
from sqlmodel import TEXT, VARCHAR, Column, Field, Relationship, SQLModel

from app.internal.base_models import BaseSQLModel
from app.utils import _AllOptionalMeta as AllOptional


class CategoryBase(SQLModel):
    name: str = Field(..., sa_column=Column(VARCHAR(255), nullable=False, index=True))
    description: Optional[str] = Field(None, sa_column=Column(TEXT))


class CategoryRelationFields(SQLModel):
    parent_id: Optional[int] = Field(None, foreign_key="category.id", nullable=True)


class Category(CategoryRelationFields, CategoryBase, BaseSQLModel, table=True):
    __tablename__ = "category"
    image: Optional[FileInfo] = Field(
        None, sa_column=Column(FileField(upload_storage="default"))
    )
    parent: Optional["Category"] = Relationship(
        sa_relationship_kwargs=dict(
            primaryjoin="remote(Category.id) == Category.parent_id"
        ),
        back_populates="childs",
    )
    movies: List["Movie"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Movie.category_id"),
        back_populates="category",
    )
    childs: List["Category"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Category.parent_id"),
        back_populates="parent",
    )


class CategoryInBase(CategoryBase):
    image: Optional[FileInfo]

    def dict(self):
        v = super().dict()
        v.update(image=self.image)
        return v


class CategoryIn(CategoryRelationFields, CategoryInBase):
    pass


def category_in_form(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    parent_id: Optional[int] = Form(None),
):
    return CategoryIn(
        name=name,
        description=description,
        image=FileInfo(content=image),
        parent_id=parent_id,
    )


class CategoryPatchBody(CategoryRelationFields, CategoryBase, metaclass=AllOptional):
    pass


class CategoryRelationsOut(SQLModel):
    movies: List["MovieOutWithoutRelations"]
    parent: Optional["CategoryOutWithoutRelations"]
    childs: List["CategoryOutWithoutRelations"]


class CategoryOutWithoutRelations(CategoryBase, BaseSQLModel):
    image: Optional[FileInfo]


class CategoryOut(
    CategoryRelationsOut, CategoryOutWithoutRelations, metaclass=AllOptional
):
    pass


from app.models.movie import Movie, MovieOutWithoutRelations

CategoryOut.update_forward_refs()
