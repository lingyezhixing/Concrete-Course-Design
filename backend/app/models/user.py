"""用户相关 Pydantic 模型。"""

import re

from pydantic import BaseModel, ConfigDict, field_validator

from app.config import (
    PASSWORD_MIN_LEN,
    USERNAME_MAX_LEN,
    USERNAME_MIN_LEN,
    USERNAME_PATTERN,
)


class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def _validate_username(cls, v: str) -> str:
        if not (USERNAME_MIN_LEN <= len(v) <= USERNAME_MAX_LEN):
            raise ValueError(f"用户名长度需 {USERNAME_MIN_LEN}-{USERNAME_MAX_LEN} 位")
        if not re.match(USERNAME_PATTERN, v):
            raise ValueError("用户名仅允许字母、数字、下划线")
        return v

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v: str) -> str:
        if len(v) < PASSWORD_MIN_LEN:
            raise ValueError(f"密码至少 {PASSWORD_MIN_LEN} 位")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic
