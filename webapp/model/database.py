from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session


Base = declarative_base()


class Database:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.session_class = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> Session:
        session = self.session_class()
        try:
            yield session
        finally:
            session.close()
