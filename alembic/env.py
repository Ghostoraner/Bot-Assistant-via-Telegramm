import sys
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from dotenv import load_dotenv

# 1. Додаємо корень проекту в PATH
sys.path.insert(0, ".")

# 2. Завантажуємо `.env`
load_dotenv()

config = context.config

# 3. Передаємо URL бази даних в Alembic
mysql_url = os.getenv("MYSQL_URL")
if mysql_url:
    # Захист на випадок, якщо в .env випадково потрапило "MYSQL_URL="
    if mysql_url.startswith("MYSQL_URL="):
        mysql_url = mysql_url.replace("MYSQL_URL=", "", 1)
    config.set_main_option("sqlalchemy.url", mysql_url)

# Налаштування логування
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Імпортуємо метадані твоїх моделей
from app.database.models import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()