from typing import Any

from app.internal.repository_manager import RepositoryManager
from app.models.auth import LoginBody
from app.models.user import UserRegister


def me(obj: Any, info):
    return None


def register(obj: Any, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.user.create(UserRegister(**input))


def login(obj: Any, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.user.login(LoginBody(**input))


def refresh_token(obj: Any, info, refresh_token: str):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.user.refresh_token(refresh_token)
