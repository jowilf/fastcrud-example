from typing import Any

from app.internal.repository_manager import RepositoryManager
from app.models.user import UserRegister


def me(obj: Any, info):
    return None


def register(obj: Any, info, input):
    repository: RepositoryManager = info.context["request"].state.repository
    return repository.user.create(UserRegister(**input))
