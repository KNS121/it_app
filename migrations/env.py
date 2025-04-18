# from logging.config import fileConfig
#
# from sqlalchemy import engine_from_config
# from sqlalchemy import pool
#
# from alembic import context
#
# import sys
# from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
#
# from app.models.models import Base
# from app.database import engine
#
# # this is the Alembic Config object, which provides
# # access to the values within the .ini file in use.
# config = context.config
#
# # Interpret the config file for Python logging.
# # This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)
#
# # add your model's MetaData object here
# # for 'autogenerate' support
# # from myapp import mymodel
# # target_metadata = mymodel.Base.metadata
# #target_metadata = None
#
# # other values from the config, defined by the needs of env.py,
# # can be acquired:
# # my_important_option = config.get_main_option("my_important_option")
# # ... etc.
#
#
# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode.
#
#     This configures the context with just a URL
#     and not an Engine, though an Engine is acceptable
#     here as well.  By skipping the Engine creation
#     we don't even need a DBAPI to be available.
#
#     Calls to context.execute() here emit the given string to the
#     script output.
#
#     """
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )
#
#     with context.begin_transaction():
#         context.run_migrations()
#
#
# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.
#
#     In this scenario we need to create an Engine
#     and associate a connection with the context.
#
#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )
#
#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )
#
#         with context.begin_transaction():
#             context.run_migrations()
#
#
# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()
#
# target_metadata = Base.metadata


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))  # Добавляем корень проекта в PYTHONPATH

from logging.config import fileConfig
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
import asyncio

# Импорт моделей и конфигурации
from app.models.models import Base
from app.database import DATABASE_URL

config = context.config
fileConfig(config.config_file_name) if config.config_file_name else None

target_metadata = Base.metadata

def run_migrations_offline():
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

async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        future=True
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True
            )
        )
        # Исправленный вызов без аргументов
        await connection.run_sync(lambda sync_conn: context.run_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())