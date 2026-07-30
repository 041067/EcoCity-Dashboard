from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
from app.database.session import Base
from app.core.config import settings
import app.models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _get_url():
    if settings.DATABASE_URL.startswith("postgresql"):
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"connect_timeout": 5, "sslmode": "require"},
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return settings.DATABASE_URL
        except Exception:
            pass
    return "sqlite:///ecocity.db"


from sqlalchemy import text

config.set_main_option("sqlalchemy.url", _get_url())
target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
