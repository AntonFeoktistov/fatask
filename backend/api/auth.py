from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
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
    return new_user


@router.post("/token", response_model=TokenResponse)
async def login(
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

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        payload = security.decode_token(refresh_token)
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid token type")

    user_oid = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_user_or_none_by_oid(db, user_oid)
    if not user:
        raise HTTPException(401, "User not found")

    new_access = security.create_access_token(
        {"sub": str(user.oid), "username": user.username}
    )
    return TokenResponse(
        access_token=new_access,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return {"message": "Successfully logged out"}
