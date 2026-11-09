import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.models import User

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_cognito_sub(self, cognito_sub: str,) -> User | None:
        try:
            statement = (select(User).where(User.cognito_sub == cognito_sub))

            user = await self.db.scalar(statement)

            logger.debug(
                "User lookup by Cognito subject completed: found=%s",
                user is not None,
            )

            return user

        except SQLAlchemyError as exc:
            logger.exception(
                "Failed to retrieve user by Cognito subject"
            )

            raise AppException(
                code="USER_FETCH_FAILED",
                message="Unable to retrieve user",
                status_code=500,
            ) from exc

    async def get_by_id(self,user_id: UUID,) -> User | None:
        try:
            statement = (select(User).where(User.id == user_id))

            return await self.db.scalar(statement)

        except SQLAlchemyError as exc:
            logger.exception(
                "Failed to retrieve user: user_id=%s",
                user_id,
            )

            raise AppException(
                code="USER_FETCH_FAILED",
                message="Unable to retrieve user",
                status_code=500,
            ) from exc

    async def create_user(self,cognito_sub: str,email: str | None = None,display_name: str | None = None,) -> User:
        try:
            user = User(
                cognito_sub=cognito_sub,
                email=email,
                display_name=display_name,
            )

            self.db.add(user)
            await self.db.flush()

            logger.info(
                "Application user created: user_id=%s",
                user.id,
            )

            return user

        except SQLAlchemyError as exc:
            logger.exception(
                "Failed to create application user"
            )

            raise AppException(
                code="USER_CREATE_FAILED",
                message="Unable to create user",
                status_code=500,
            ) from exc