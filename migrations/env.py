from logging.config import fileConfig

import autoflake
from alembic import context
from alembic.script import write_hooks
from loguru import logger
from sqlalchemy import engine_from_config, pool

from app.config import config as AppConfig
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from app.internal.base_models import BaseSQLModel
from app.models.author import Author
from app.models.author_profile import AuthorProfile
from app.models.category import Category
from app.models.manager import Manager
from app.models.many_to_many import Friends_ofFriendsLink, MoviesAuthorsLink
from app.models.movie import Movie
from app.models.movie_preview import MoviePreview
from app.models.user import User

_MODELS = [
    Movie,
    User,
    MoviePreview,
    Category,
    Author,
    AuthorProfile,
    Manager,
    MoviesAuthorsLink,
    Friends_ofFriendsLink,
]

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", AppConfig.db.url())

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseSQLModel.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def process_revision_directives(_, __, directives):
    script = directives[0]
    if script.upgrade_ops.is_empty():
        logger.debug("Nothing to update")
        directives[:] = []


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


@write_hooks.register("add_imports")
def add_imports(filename, options):
    text = open(filename).read()
    with open(filename, "w") as to_write:
        text = f"import sqlmodel\nimport app\n{text}"
        text = autoflake.fix_code(text, remove_all_unused_imports=True)
        to_write.write(text)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
