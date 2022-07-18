from contextlib import contextmanager

from sqlmodel import Session
from starlette.templating import Jinja2Templates

from app.database import db
from app.internal.repository_manager import RepositoryManager


def get_templates():
    return Jinja2Templates("templates")


def repository_manager():
    session: Session = Session(db.engine, autoflush=False)
    try:
        yield RepositoryManager(session)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@contextmanager
def repository_manager_ctx():
    session: Session = Session(db.engine, autoflush=False)
    try:
        yield RepositoryManager(session)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
