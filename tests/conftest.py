"""
conftest.py contains global configurations that are available to all tests.
"""
import os
from dotenv import load_dotenv, find_dotenv
import pytest
from webapp.model import Database, Base

load_dotenv(find_dotenv())


@pytest.fixture(scope="function", name="database")
def fixture_database():
    db = Database(os.environ['DATABASE_URL'])
    with db.get_session() as session:
        yield session
    Base.metadata.drop_all(db.engine)
