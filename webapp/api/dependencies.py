import os
from sqlalchemy.orm import Session
from webapp.model.database import Database


DATABASE_URL = os.environ["DATABASE_URL"]
database = Database(DATABASE_URL)
database.create_tables()


def get_db() -> Session:
    with database.get_session() as session:
        yield session
