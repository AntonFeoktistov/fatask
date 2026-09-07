from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core import security
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.core.exceptions import UserAlreadyExistsException
from backend.models.user import User
from backend.repositories.user_repo import UserRepository
from backend.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
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


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    login_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_or_none_by_email(login_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = security.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token = security.create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    payload = security.decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user_repo = UserRepository(db)
    user = await user_repo.get_user_or_none_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = security.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    new_refresh_token = security.create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
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
