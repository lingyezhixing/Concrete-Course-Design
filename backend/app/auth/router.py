"""鉴权路由：注册/登录/当前用户。"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.auth.repository import UsernameAlreadyExists, create_user, delete_user, get_by_username
from app.config import TOKEN_EXPIRE_DAYS
from app.models.user import Token, UserCreate, UserLogin, UserPublic
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

_EXPIRES_IN = TOKEN_EXPIRE_DAYS * 86400


def _issue_token(user: dict) -> Token:
    return Token(
        access_token=create_access_token(user["id"]),
        token_type="bearer",
        expires_in=_EXPIRES_IN,
        user=UserPublic(**user),
    )


@router.post("/register", response_model=Token)
def register(payload: UserCreate) -> Token:
    try:
        user = create_user(payload.username, payload.password)
    except UsernameAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="用户名已存在"
        )
    return _issue_token(user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin) -> Token:
    row = get_by_username(payload.username)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户名不存在"
        )
    if not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误"
        )
    return _issue_token(
        {
            "id": row["id"],
            "username": row["username"],
            "created_at": row["created_at"],
        }
    )


@router.get("/me", response_model=UserPublic)
def me(current_user: dict = Depends(get_current_user)) -> UserPublic:
    return UserPublic(**current_user)


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(current_user: dict = Depends(get_current_user)) -> None:
    """注销账户：删除当前用户（及未来全部按用户隔离的数据）。"""
    delete_user(current_user["id"])
