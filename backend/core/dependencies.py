import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import decode_token, oauth2_scheme
from backend.models.user import User
from backend.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    logger.info(
        "get_current_user: received token (len=%d, prefix=%s...)",
        len(token),
        token[:20],
    )

    try:
        payload = decode_token(token)
        logger.info("get_current_user: decoded payload = %s", payload)
    except JWTError as e:
        logger.warning("get_current_user: JWT decode failed: %s", e)
        raise credentials_exception

    token_type = payload.get("type")
    logger.info("get_current_user: token type = %r", token_type)
    if token_type != "access":
        logger.warning(
            "get_current_user: wrong token type %r (expected 'access')", token_type
        )
        raise credentials_exception

    sub = payload.get("sub")
    logger.info("get_current_user: sub = %r (python type: %s)", sub, type(sub).__name__)
    if sub is None:
        logger.warning("get_current_user: sub is missing")
        raise credentials_exception

    try:
        user_id = int(sub)
        logger.info("get_current_user: parsed user_id = %d", user_id)
    except (TypeError, ValueError) as e:
        logger.warning("get_current_user: cannot parse sub=%r to int: %s", sub, e)
        raise credentials_exception

    user = await UserRepository(db).get_user_or_none_by_id(user_id)
    logger.info("get_current_user: db lookup result = %r", user)

    if user is None:
        logger.warning("get_current_user: user not found for id=%d", user_id)
        raise credentials_exception

    logger.info(
        "get_current_user: authenticated user id=%d username=%s", user.id, user.username
    )
    return user
