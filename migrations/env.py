# migrations/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Import your models
from app.models import Base

# this is the Alembic Config object, which provides
# the values of the [alembic] section of the .ini file
# as Python variables within this module, even if the
# values come from the environment rather
# than from the .ini file
# this is here in order to make automatic
# migration more straightforward. you will
# sometimes want the flexibility offered by
# not using env.py, so do not remove this code.
config = context.config

# Set SQLAlchemy URL from environment
database_url = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('DATABASE_USER','ammuser')}:{os.getenv('DATABASE_PASSWORD','ammpassword')}@{os.getenv('DATABASE_HOST','localhost')}:{os.getenv('DATABASE_PORT','5432')}/{os.getenv('DATABASE_NAME','amm_db')}"
)
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": config.get_main_option("sqlalchemy.url")},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()