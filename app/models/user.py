import re
from datetime import datetime
from typing import List, Optional

from common.types import PhoneNumber
from pydantic import EmailStr, validator
from sqlalchemy import func
from sqlmodel import DATETIME, JSON, VARCHAR, Column, Field, SQLModel

from app.internal.base_models import BaseSQLModel
from app.utils import _AllOptionalMeta as AllOptional


class UserBase(SQLModel):
    username: str = Field(
        ...,
        sa_column=Column(VARCHAR(255), nullable=False, unique=True, index=True),
        min_length=3,
    )
    phonenumber: Optional[PhoneNumber] = Field(
        None, sa_column=Column(VARCHAR(15), index=True)
    )
    email: Optional[EmailStr] = Field(None, sa_column=Column(VARCHAR(255), index=True))
    roles: Optional[List[str]] = Field([], sa_column=Column(JSON))


class UserRelationFields(SQLModel):
    pass


class User(UserRelationFields, UserBase, BaseSQLModel, table=True):
    __tablename__ = "user"
    password: str = Field(
        ..., sa_column=Column(VARCHAR(255), nullable=False, index=True)
    )
    date_joined: Optional[datetime] = Field(
        None,
        sa_column=Column(DATETIME(timezone=True), nullable=False, default=func.now()),
    )


class UserInBase(UserBase):
    pass


class UserRegister(UserInBase):
    password: str = Field(..., min_length=8, max_length=20)

    @validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("ensure this value has no spaces")
        if not any(map(str.isupper, v)):
            raise ValueError("ensure this value contains at least one uppercase letter")
        if not any(map(str.islower, v)):
            raise ValueError("ensure this value contains at least one lowercase letter")
        if sum(map(str.isdigit, v)) < 1:
            raise ValueError("ensure this value contains at least 1 digits")
        if re.search(r"[@&%$()=!?*+-.,:;]", v) is None:
            raise ValueError(
                "ensure this value has at least one special characters (@&%$()=!?*+-.,:;)"
            )
        return v


class UserIn(UserRelationFields, UserInBase):
    pass


class UserPatchBody(UserIn, metaclass=AllOptional):
    pass


class UserRelationsOut(BaseSQLModel):
    pass


class UserOutWithoutRelations(UserBase, BaseSQLModel):
    date_joined: Optional[datetime]


class UserOut(UserRelationsOut, UserOutWithoutRelations, metaclass=AllOptional):
    pass


UserOut.update_forward_refs()
