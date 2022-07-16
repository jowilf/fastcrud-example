from asyncio.log import logger

from alembic import command
from alembic.config import Config
from sqlalchemy_utils import create_database, database_exists
from sqlmodel import create_engine

from app.config import config as app_config


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(
            app_config.db.url(), echo=(app_config.env != "prod")
        )
        self.config = Config("alembic.ini")

    def migrate_schema(self):
        if not database_exists(self.engine.url):
            try:
                create_database(self.engine.url)
                logger.debug("Database created!")
            except Exception as e:
                logger.exception("Error encounter while created database", e)
        command.upgrade(self.config, "head")
        command.revision(self.config, autogenerate=True)
        command.upgrade(self.config, "head")

    def reset_database(self):
        command.downgrade(self.config, "base")
        command.upgrade(self.config, "head")
