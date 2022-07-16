from typing import List, Optional

from fastapi import Depends, HTTPException, Security, security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.config import config
from app.dependencies import repository_manager
from app.internal.repository_manager import RepositoryManager

security = HTTPBearer()


def authorize(roles: Optional[List[str]] = []):
    def auth_wrapper(
        credentials: HTTPAuthorizationCredentials = Security(security),
        repository: RepositoryManager = Depends(repository_manager),
    ):
        try:
            payload = jwt.decode(
                credentials.credentials, config.jwt.secret, config.jwt.algorithm
            )
            if payload.get("type") != "access_token":
                raise JWTError()
            user = repository.user.find_by_id(payload.get("sub"))
            if not user.has_permission(roles):
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=f"Access Forbidden")
            return user
        except JWTError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials",
            )

    return auth_wrapper
