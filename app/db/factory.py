from app.core.config import get_settings
from app.db.interfaces.base import BaseDatabase
from app.db.interfaces.database import SQLAlchemyDatabase
from app.db.interfaces.config import DatabaseConfig
from app.db import models  # noqa: F401
from sqlalchemy.engine import URL

async def make_database() -> BaseDatabase:
    settings = get_settings()
    database_url = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.db_username,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
).render_as_string(hide_password=False)
    

    config = DatabaseConfig(
        database_url=database_url,
        echo_sql=settings.echo_sql,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
    )

    database = SQLAlchemyDatabase(config=config)
    await database.startup()
    return database