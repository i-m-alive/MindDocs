# alembic/env.py

import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ✅ Add .env support to load DATABASE_URL
from dotenv import load_dotenv
load_dotenv()

# ✅ Add project base directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Alembic Config object for logging and DB URL override
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Read DATABASE_URL from .env and set to config
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set in the .env file")

# ✅ Escape % characters for compatibility with Alembic config parser
escaped_url = database_url.replace('%', '%%')
config.set_main_option("sqlalchemy.url", escaped_url)

# ✅ Import models and metadata
from app.utils.database import Base
from app.auth.models import User
from app.models.documents import Document
from app.models.chat import ChatHistory
from app.models.translation import TranslationHistory
from app.models.summary import SummaryHistory
from app.models.extraction import DocumentExtraction

# ✅ Needed for Alembic autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode without DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True  # Optional: detect type changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True  # Optional: detect type changes
        )

        with context.begin_transaction():
            context.run_migrations()


# ✅ Dispatch to correct mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
