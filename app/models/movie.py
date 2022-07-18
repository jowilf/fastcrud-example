from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import func
from sqlmodel import (DATE, DATETIME, INT, JSON, TEXT, VARCHAR, Column, Field,
                      Relationship, SQLModel)

from app.internal.base_models import BaseSQLModel
from app.models.many_to_many import MoviesAuthorsLink
from app.utils import _AllOptionalMeta as AllOptional


class MovieBase(SQLModel):
    name: str = Field(
        ..., sa_column=Column(VARCHAR(255), nullable=False, index=True), min_length=3
    )
    description: Optional[str] = Field(None, sa_column=Column(TEXT))
    watch_count: Optional[int] = Field(None, sa_column=Column(INT, index=True), ge=0.0)
    tags: Optional[List[str]] = Field(
        [], sa_column=Column(JSON), max_items=10, max_length=100
    )
    release_date: Optional[date] = Field(None, sa_column=Column(DATE, index=True))


class MovieRelationFields(SQLModel):
    category_id: Optional[int] = Field(None, foreign_key="category.id", nullable=True)


class Movie(MovieRelationFields, MovieBase, BaseSQLModel, table=True):
    __tablename__ = "movie"
    created_at: Optional[datetime] = Field(
        None,
        sa_column=Column(DATETIME(timezone=True), nullable=False, default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        None, sa_column=Column(DATETIME(timezone=True), onupdate=func.now())
    )
    category: Optional["Category"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Movie.category_id"),
        back_populates="movies",
    )
    preview: Optional["MoviePreview"] = Relationship(
        sa_relationship_kwargs=dict(
            foreign_keys="MoviePreview.movie_id", uselist=False
        ),
        back_populates="movie",
    )
    authors: List["Author"] = Relationship(
        back_populates="movies", link_model=MoviesAuthorsLink
    )


class MovieInBase(MovieBase):
    pass


class MovieIn(MovieRelationFields, MovieInBase):
    pass


class MoviePatchBody(MovieIn, metaclass=AllOptional):
    pass


class MovieRelationsOut(SQLModel):
    preview: Optional["MoviePreviewOutWithoutRelations"]
    category: Optional["CategoryOutWithoutRelations"]
    authors: List["AuthorOutWithoutRelations"]


class MovieOutWithoutRelations(MovieBase, BaseSQLModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class MovieOut(MovieRelationsOut, MovieOutWithoutRelations, metaclass=AllOptional):
    pass


from app.models.author import Author, AuthorOutWithoutRelations
from app.models.category import Category, CategoryOutWithoutRelations
from app.models.movie_preview import (MoviePreview,
                                      MoviePreviewOutWithoutRelations)

MovieOut.update_forward_refs()
