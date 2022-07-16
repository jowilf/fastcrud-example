from typing import Optional

from sqlmodel import Field

from app.internal.base_models import BaseTable


class MoviesAuthorsLink(BaseTable, table=True):
    __tablename__ = "movies_authors_link"
    movie_id: Optional[int] = Field(
        None, foreign_key="movie.id", primary_key=True, nullable=False
    )
    author_id: Optional[int] = Field(
        None, foreign_key="author.id", primary_key=True, nullable=False
    )


class Friends_ofFriendsLink(BaseTable, table=True):
    __tablename__ = "friends_of_friends_link"
    author1_id: Optional[int] = Field(
        None, foreign_key="author.id", primary_key=True, nullable=False
    )
    author2_id: Optional[int] = Field(
        None, foreign_key="author.id", primary_key=True, nullable=False
    )
