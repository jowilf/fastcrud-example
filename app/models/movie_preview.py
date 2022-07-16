from typing import List, Optional

from common.types import FileField, FileInfo
from fastapi import File, Form, UploadFile
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.internal.base_models import BaseSQLModel
from app.utils import _AllOptionalMeta as AllOptional


class MoviePreviewBase(SQLModel):
    tags: Optional[List[str]] = Field(None, sa_column=Column(JSON))


class MoviePreviewRelationFields(SQLModel):
    movie_id: Optional[int] = Field(
        None, foreign_key="movie.id", nullable=True, sa_column_kwargs=dict(unique=True)
    )


class MoviePreview(
    MoviePreviewRelationFields, MoviePreviewBase, BaseSQLModel, table=True
):
    __tablename__ = "movie_preview"
    images: Optional[List[FileInfo]] = Field(
        [], sa_column=Column(FileField(upload_storage="default", is_array=True))
    )
    movie: Optional["Movie"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="MoviePreview.movie_id"),
        back_populates="preview",
    )


class MoviePreviewInBase(MoviePreviewBase):
    images: Optional[List[FileInfo]]

    def dict(self):
        v = super().dict()
        v.update(images=self.images)
        return v


class MoviePreviewIn(MoviePreviewRelationFields, MoviePreviewInBase):
    pass


def movie_preview_in_form(
    images: Optional[List[UploadFile]] = File([]),
    tags: Optional[List[str]] = Form(None),
    movie_id: Optional[int] = Form(None),
):
    return MoviePreviewIn(
        images=[FileInfo(content=file) for file in images], tags=tags, movie_id=movie_id
    )


class MoviePreviewPatchBody(
    MoviePreviewRelationFields, MoviePreviewBase, metaclass=AllOptional
):
    pass


class MoviePreviewRelationsOut(BaseSQLModel):
    movie: Optional["MovieOutWithoutRelations"]


class MoviePreviewOutWithoutRelations(MoviePreviewBase, BaseSQLModel):
    images: Optional[List[FileInfo]]


class MoviePreviewOut(
    MoviePreviewRelationsOut, MoviePreviewOutWithoutRelations, metaclass=AllOptional
):
    pass


from app.models.movie import Movie, MovieOutWithoutRelations

MoviePreviewOut.update_forward_refs()
