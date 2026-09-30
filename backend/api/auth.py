import uuid
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core import security
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.core.exceptions import (
    NotCorrectCredentialsException,
    UserAlreadyExistsException,
)
from backend.models.user import User
from backend.repositories.user_repo import UserRepository
from backend.schemas.user import (
    TokenResponse,
    UserCreate,
    UserResponse,
)
from backend.tasks.email_tasks import send_welcome_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = UserRepository(db)
    existing_email = await user_repo.get_user_or_none_by_email(user_data.email)
    if existing_email:
        raise UserAlreadyExistsException()

    existing_username = await user_repo.get_user_or_none_by_username(user_data.username)
    if existing_username:
        raise UserAlreadyExistsException()

    new_user = await user_repo.create_user(user_data)

    await db.commit()
    await db.refresh(new_user)
    send_welcome_email.delay(new_user.email, new_user.username)
    return new_user


@router.post("/token", response_model=TokenResponse)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_or_none_by_username(form_data.username)

    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise NotCorrectCredentialsException()

    access_token = security.create_access_token(
        data={"sub": str(user.oid), "username": user.username}
    )
    refresh_token = security.create_refresh_token(data={"sub": str(user.oid)})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 3600,
        path="/",
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    if refresh_token is None:
        raise HTTPException(401, "No refresh token")

    try:
        payload = security.decode_token(refresh_token)
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid token type")

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(401, "Invalid refresh token")

    try:
        user_oid = uuid.UUID(sub)
    except (TypeError, ValueError):
        raise HTTPException(401, "Invalid refresh token")

    user_repo = UserRepository(db)
    user = await user_repo.get_user_or_none_by_oid(user_oid)
    if not user:
        raise HTTPException(401, "User not found")

    new_access = security.create_access_token(
        data={"sub": str(user.oid), "username": user.username}
    )

    new_refresh = security.create_refresh_token(data={"sub": str(user.oid)})
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 3600,
        path="/",
    )
    return TokenResponse(
        access_token=new_access,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.post("/logout")
async def logout(
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
):
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Successfully logged out"}
