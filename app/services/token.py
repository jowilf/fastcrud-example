from datetime import datetime, timedelta

from jose import jwt

from app.config import config


def create_access_token(id: int):
    expire = datetime.utcnow() + timedelta(seconds=config.jwt.token_ttl)
    token = jwt.encode(
        dict(sub=str(id), type="access_token", exp=expire),
        config.jwt.secret,
        config.jwt.algorithm,
    )
    return token


def create_refresh_token(id: int):
    expire = datetime.utcnow() + timedelta(seconds=config.jwt.refresh_token_ttl)
    token = jwt.encode(
        dict(sub=str(id), type="refresh_token", exp=expire),
        config.jwt.secret,
        config.jwt.algorithm,
    )
    return token
