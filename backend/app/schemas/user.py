from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    nickname: str = Field(min_length=2, max_length=50)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    nickname: str | None = Field(default=None, min_length=2, max_length=50)
    bio: str | None = Field(default=None, max_length=200)
    profile_image_url: str | None = Field(default=None, max_length=500)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nickname: str
    bio: str | None
    profile_image_url: str | None
    created_at: datetime


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=1)
