from typing import Any, TypeVar

from sqlmodel import Session

from app.repositories.author import AuthorRepository
from app.repositories.author_profile import AuthorProfileRepository
from app.repositories.category import CategoryRepository
from app.repositories.manager import ManagerRepository
from app.repositories.movie import MovieRepository
from app.repositories.movie_preview import MoviePreviewRepository
from app.repositories.user import UserRepository

from .base_models import BaseSQLModel

T = TypeVar("T", bound=BaseSQLModel)


class RepositoryManager:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.movie = MovieRepository(self)
        self.user = UserRepository(self)
        self.movie_preview = MoviePreviewRepository(self)
        self.category = CategoryRepository(self)
        self.author = AuthorRepository(self)
        self.author_profile = AuthorProfileRepository(self)
        self.manager = ManagerRepository(self)

    def remove(self, instance: T) -> None:
        self.session.delete(instance)
        self.session.commit()

    def add(self, instance: T) -> None:
        self.session.add(instance)

    def save(self, instance: T) -> T:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def save_all(self, instances: Any):
        self.session.add_all(instances)
        self.session.commit()
