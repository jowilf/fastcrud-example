from typing import List, Optional

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED

from app.config import config
from app.dependencies import repository_manager
from app.internal.repository_manager import RepositoryManager

api_key_header = APIKeyHeader(name="Authorization")


def authenticated_user(with_roles: Optional[List[str]] = None):
    credential_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail=f"Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    def get_auth_user(
        token: str = Depends(api_key_header),
        repository: RepositoryManager = Depends(repository_manager),
    ):
        try:
            payload = jwt.decode(token, config.jwt.secret, config.jwt.algorithm)
            if payload.get("type") != "access_token":
                raise JWTError()
            user = repository.user.find_by_id(payload.get("sub"))
            if with_roles is not None:
                for role in with_roles:
                    if role not in user.roles:
                        raise credential_exception
            return user
        except JWTError as e:
            raise credential_exception

    return get_auth_user
