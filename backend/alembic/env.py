import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Alembic Config object
config = context.config

# Setup Python logging from config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your SQLAlchemy Base
from database import Base  # Make sure this points to your database.py
target_metadata = Base.metadata

# --------------------------
# Offline migrations
# --------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# --------------------------
# Online migrations
# --------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# --------------------------
# Run migrations based on mode
# --------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
