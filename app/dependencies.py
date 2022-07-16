from fastapi import Depends
from sqlmodel import Session
from starlette.templating import Jinja2Templates

from app.database import Database
from app.internal.repository_manager import RepositoryManager


def get_session():
    session: Session = Session(Database().engine, autoflush=False)
    try:
        yield session
    except Exception as e:
        # app_logger.exception(f"Session rollback because of exception", e)
        session.rollback()
        raise e
    finally:
        session.close()


def get_templates():
    return Jinja2Templates("templates")


def repository_manager(session: Session = Depends(get_session)):
    return RepositoryManager(session)
