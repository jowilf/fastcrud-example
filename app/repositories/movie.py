from typing import TYPE_CHECKING, List, Optional, Union

from app.filters.movie import MovieFilter, MovieOrderBy
from app.internal.base_repository import BaseRepository
from app.internal.filters import PaginationQuery
from app.internal.response import CountResponse
from app.models.movie import Movie, MovieIn, MoviePatchBody

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class MovieRepository(BaseRepository[Movie]):
    def __init__(self, rm: "RepositoryManager") -> None:
        super().__init__(Movie, rm.session)
        self.rm = rm

    def find_all(
        self,
        pagination: PaginationQuery = PaginationQuery(),
        where: Optional[MovieFilter] = None,
        order_by: Optional[MovieOrderBy] = None,
        count=False,
    ) -> Union[List[Movie], int]:
        return super().find_all(pagination, where, order_by, count)

    def find_one(self, where: Optional[MovieFilter]) -> Optional[Movie]:
        return super().find_one(where)

    def create(self, movie_in: MovieIn) -> Movie:
        assert (
            movie_in.category_id is None
            or self.rm.category.find_by_id(movie_in.category_id) is not None
        )
        movie = Movie(**movie_in.dict())
        return self.save(movie)

    def update(self, id: int, movie_in: MovieIn) -> Movie:
        movie = self.find_by_id(id)
        assert (
            movie_in.category_id is None
            or self.rm.category.find_by_id(movie_in.category_id) is not None
        )
        movie.update(movie_in.dict())
        return self.save(movie)

    def patch(self, id: int, movie_in: MoviePatchBody) -> Movie:
        movie = self.find_by_id(id)
        assert (
            movie_in.category_id is None
            or self.rm.category.find_by_id(movie_in.category_id) is not None
        )
        movie.update(movie_in.dict(exclude_unset=True))
        return self.save(movie)

    def delete(self, where: Optional[MovieFilter]) -> CountResponse:
        return super().delete(where)
