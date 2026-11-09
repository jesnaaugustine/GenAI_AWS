from app.core.config import get_settings
from app.db.interfaces.base import BaseDatabase
from app.db.interfaces.database import SQLAlchemyDatabase,Base
from app.db.interfaces.config import DatabaseConfig
from sqlalchemy import inspect
from app.db import models  # noqa: F401
import logging
from sqlalchemy.engine import URL

logger = logging.getLogger(__name__)
def make_database() -> BaseDatabase:
    settings = get_settings()
    database_url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.db_username,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    

    config = DatabaseConfig(
        database_url=database_url,
        echo_sql=settings.echo_sql,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
    )

    database = SQLAlchemyDatabase(config=config)
    return database

def init_db() -> None:
    db = make_database()
    try:   
        db.startup()
        logger.info("Database initialized successfully")
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        Base.metadata.create_all(bind=db.engine)
        
        updated_tables = inspector.get_table_names()
        new_tables = set(updated_tables) - set(existing_tables)

        if new_tables:
            logger.info(f"Created new tables: {', '.join(new_tables)}")
        else:
            logger.info("All tables already exist - no new tables created")

        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")      