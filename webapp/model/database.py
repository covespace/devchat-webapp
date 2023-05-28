from contextlib import contextmanager
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session


Base = declarative_base()


class Database:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.session_class = sessionmaker(bind=self.engine)

        alembic_cfg = Config('alembic.ini')
        alembic_cfg.set_main_option('sqlalchemy.url', database_url)
        upgrade(alembic_cfg, 'head')

    @contextmanager
    def get_session(self) -> Session:
        session = self.session_class()
        try:
            yield session
        finally:
            session.close()
