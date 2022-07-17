from typing import List, Optional

from fastapi import Depends, HTTPException, security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.dependencies import repository_manager
from app.filters.user import UserFilter
from app.internal.repository_manager import RepositoryManager
from app.services.password import verify_password

security = HTTPBasic()


def authorize(roles: Optional[List[str]] = []):
    def auth_wrapper(
        credentials: HTTPBasicCredentials = Depends(security),
        repository: RepositoryManager = Depends(repository_manager),
    ):
        user = repository.user.find_one(UserFilter(username=credentials.username))
        if user is None or not verify_password(credentials.password, user.password):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials",
            )
        if not user.has_permission(roles):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail=f"Access Forbidden"
            )
        return user

    return auth_wrapper
