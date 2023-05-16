import os
from sqlalchemy.orm import Session
from webapp.model.database import Database


database = None


def get_database():
    """
    Get the database instance.
    :return: the database instance
    """
    global database
    if database is None:
        db_url = os.environ["DATABASE_URL"]
        database = Database(db_url)
    return database


def init_tables():
    """
    Initialize the database tables.
    """
    db = get_database()
    return db.create_tables()


def get_db() -> Session:
    global database
    if database is None:
        db_url = os.environ["DATABASE_URL"]
        database = Database(db_url)
    with database.get_session() as session:
        yield session
