import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.models import User
from app.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self,
        db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        # print("UserService initialized with database session:", db)

    async def get_or_create_user(self,cognito_sub: str) -> User:
        try:
            user = await self.user_repository.get_by_cognito_sub(cognito_sub)

            if user is not None:
                logger.debug(
                    "Application user found: user_id=%s",
                    user.id,
                )
                return user
            print('before user creation')
            user = await self.user_repository.create_user(cognito_sub=cognito_sub)

            await self.db.commit()

            logger.info(
                "Application user provisioned: user_id=%s",
                user.id,
            )
            return user

        except Exception as exc:
            await self.db.rollback()
            logger.exception(
                "Failed to get or create application user"
            )
            raise AppException(
                        code="INVALID USER",
                        message="Invalid user details",
                        status_code=500,
                    ) from exc