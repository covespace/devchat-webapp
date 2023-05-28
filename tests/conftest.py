"""
conftest.py contains global configurations that are available to all tests.
"""
import os
import secrets
import pytest
from webapp.model import Database, Base

# Generate a 32-byte random secret key for HS256
os.environ['JWT_SECRET_KEY'] = secrets.token_hex(32)

if not os.getenv('DATABASE_URL'):
    # For local testing
    os.environ['DATABASE_URL'] = "postgresql://merico@localhost/devchat"


@pytest.fixture(scope="function", name="database")
def fixture_database():
    db = Database(os.environ['DATABASE_URL'])
    with db.get_session() as session:
        yield session
    Base.metadata.drop_all(db.engine)
