from pydantic import BaseModel, Field


class LoginBody(BaseModel):
    username: str = Field(..., min_length=3)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
