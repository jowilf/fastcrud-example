from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import func
from sqlmodel import (DATE, DATETIME, TIME, VARCHAR, Column, Enum, Field,
                      Relationship, SQLModel)

from app.internal.base_models import BaseSQLModel
from app.models import enums
from app.models.many_to_many import Friends_ofFriendsLink, MoviesAuthorsLink
from app.utils import _AllOptionalMeta as AllOptional


class AuthorBase(SQLModel):
    lastname: str = Field(
        ..., sa_column=Column(VARCHAR(255), nullable=False, index=True)
    )
    firstname: str = Field(
        ..., sa_column=Column(VARCHAR(255), nullable=False, index=True)
    )
    sex: Optional[enums.Gender] = Field(
        enums.Gender.male, sa_column=Column(Enum(enums.Gender), index=True)
    )
    birthday: Optional[date] = Field(None, sa_column=Column(DATE, index=True))
    wakeup_time: Optional[time] = Field(None, sa_column=Column(TIME, index=True))
    wakeup_day: Optional[datetime] = Field(None, sa_column=Column(DATETIME, index=True))


class AuthorRelationFields(SQLModel):
    manager_id: Optional[int] = Field(None, foreign_key="manager.id", nullable=True)
    profile_id: Optional[int] = Field(
        None,
        foreign_key="author_profile.id",
        nullable=True,
        sa_column_kwargs=dict(unique=True),
    )


class Author(AuthorRelationFields, AuthorBase, BaseSQLModel, table=True):
    __tablename__ = "author"
    created_at: Optional[datetime] = Field(
        None,
        sa_column=Column(DATETIME(timezone=True), nullable=False, default=func.now()),
    )
    updated_at: Optional[datetime] = Field(
        None, sa_column=Column(DATETIME(timezone=True), onupdate=func.now())
    )
    manager: Optional["Manager"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Author.manager_id"),
        back_populates="authors",
    )
    profile: Optional["AuthorProfile"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="Author.profile_id"),
        back_populates="author",
    )
    movies: List["Movie"] = Relationship(
        back_populates="authors", link_model=MoviesAuthorsLink
    )
    friends: List["Author"] = Relationship(
        back_populates="friends_of",
        link_model=Friends_ofFriendsLink,
        sa_relationship_kwargs=dict(
            primaryjoin="Author.id==Friends_ofFriendsLink.author1_id",
            secondaryjoin="Author.id==Friends_ofFriendsLink.author2_id",
        ),
    )
    friends_of: List["Author"] = Relationship(
        back_populates="friends",
        link_model=Friends_ofFriendsLink,
        sa_relationship_kwargs=dict(
            primaryjoin="Author.id==Friends_ofFriendsLink.author2_id",
            secondaryjoin="Author.id==Friends_ofFriendsLink.author1_id",
        ),
    )


class AuthorInBase(AuthorBase):
    pass


class AuthorIn(AuthorRelationFields, AuthorInBase):
    pass


class AuthorPatchBody(AuthorIn, metaclass=AllOptional):
    pass


class AuthorRelationsOut(SQLModel):
    manager: Optional["ManagerOutWithoutRelations"]
    profile: Optional["AuthorProfileOutWithoutRelations"]
    movies: List["MovieOutWithoutRelations"]
    friends: List["AuthorOutWithoutRelations"]
    friends_of: List["AuthorOutWithoutRelations"]


class AuthorOutWithoutRelations(AuthorBase, BaseSQLModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class AuthorOut(AuthorRelationsOut, AuthorOutWithoutRelations, metaclass=AllOptional):
    pass


from app.models.author_profile import (AuthorProfile,
                                       AuthorProfileOutWithoutRelations)
from app.models.manager import Manager, ManagerOutWithoutRelations
from app.models.movie import Movie, MovieOutWithoutRelations

AuthorOut.update_forward_refs()
