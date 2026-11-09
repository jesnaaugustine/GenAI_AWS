import logging
from contextlib import asynccontextmanager
from typing import Generator, Optional


from requests import session
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker,DeclarativeBase

from app.db.interfaces.base import BaseDatabase
from app.db.interfaces.config import DatabaseConfig

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass    

class SQLAlchemyDatabase(BaseDatabase):
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None

    async def startup(self) -> None:
        """Initialize the database connection."""
        logger.info("Starting up the database connection")
        try:
            # self.engine = create_engine(
            #     self.config.database_url,
            #     echo=self.config.echo_sql,
            #     pool_size=self.config.pool_size,
            #     max_overflow=self.config.max_overflow,
            # )
            self.engine = create_async_engine(self.config.database_url,pool_size=self.config.pool_size, max_overflow=self.config.max_overflow, echo=self.config.echo_sql,pool_pre_ping=True,pool_recycle=3600)
            self.session_factory = async_sessionmaker(bind=self.engine,class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
                )
            logger.info("Database connection established")
            


        except Exception as e:
            logger.error("Failed to establish database connection")
            raise

    async def teardown(self) -> None:
        """Close the database connection."""
        if self.engine:
            logger.info("Tearing down the database connection")
            await self.engine.dispose()
            logger.info("Database connection closed")

    @asynccontextmanager
    async def get_session(self):
        """Get a database session."""
        if self.session_factory is None:
            raise RuntimeError("Database session factory is not initialized. Call startup() first.")

        session: AsyncSession = self.session_factory()
        
        try:
            print('before____________')
            logger.info("SQLAlchemy session created successfully: %s",session,  )
            session.execute(text("SELECT 1"))
            
            logger.info("Database connection test successful")
            yield session
            print("Session commit----------")
        except Exception as e:
            session.rollback()
            logger.exception("Session rollback due to exception")
            raise
        finally:
            session.close()