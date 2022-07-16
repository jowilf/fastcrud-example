from typing import TYPE_CHECKING, List, Optional, Union

from app.filters.movie_preview import MoviePreviewFilter, MoviePreviewOrderBy
from app.internal.base_repository import BaseRepository
from app.internal.filters import PaginationQuery
from app.internal.response import CountResponse
from app.models.movie_preview import (MoviePreview, MoviePreviewIn,
                                      MoviePreviewPatchBody)

if TYPE_CHECKING:
    from app.internal.repository_manager import RepositoryManager


class MoviePreviewRepository(BaseRepository[MoviePreview]):
    def __init__(self, rm: "RepositoryManager") -> None:
        super().__init__(MoviePreview, rm.session)
        self.rm = rm

    def find_all(
        self,
        pagination: PaginationQuery = PaginationQuery(),
        where: Optional[MoviePreviewFilter] = None,
        order_by: Optional[MoviePreviewOrderBy] = None,
        count=False,
    ) -> Union[List[MoviePreview], int]:
        return super().find_all(pagination, where, order_by, count)

    def find_one(self, where: Optional[MoviePreviewFilter]) -> Optional[MoviePreview]:
        return super().find_one(where)

    def create(self, movie_preview_in: MoviePreviewIn) -> MoviePreview:
        if movie_preview_in.movie_id is not None:
            movie = self.rm.movie.find_by_id(movie_preview_in.movie_id)
            movie.preview = None
            self.rm.save(movie)
        movie_preview = MoviePreview(**movie_preview_in.dict())
        return self.save(movie_preview)

    def update(self, id: int, movie_preview_in: MoviePreviewIn) -> MoviePreview:
        movie_preview = self.find_by_id(id)
        if movie_preview_in.movie_id is not None:
            movie = self.rm.movie.find_by_id(movie_preview_in.movie_id)
            movie.preview = None
            self.rm.save(movie)
        movie_preview.update(movie_preview_in.dict())
        return self.save(movie_preview)

    def patch(self, id: int, movie_preview_in: MoviePreviewPatchBody) -> MoviePreview:
        movie_preview = self.find_by_id(id)
        if movie_preview_in.movie_id is not None:
            movie = self.rm.movie.find_by_id(movie_preview_in.movie_id)
            movie.preview = None
            self.rm.save(movie)
        movie_preview.update(movie_preview_in.dict(exclude_unset=True))
        return self.save(movie_preview)

    def delete(self, where: Optional[MoviePreviewFilter]) -> CountResponse:
        return super().delete(where)
