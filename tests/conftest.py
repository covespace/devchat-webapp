"""
conftest.py contains global configurations that are available to all tests.
"""
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import pytest
from webapp.model import Database, Base


private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

os.environ['JWT_PRIVATE_KEY'] = private_pem.decode('utf-8')
os.environ['JWT_PUBLIC_KEY'] = public_pem.decode('utf-8')


@pytest.fixture(scope="function", name="database")
def fixture_database(postgresql):
    connection = f"postgresql+psycopg://{postgresql.info.user}:@{postgresql.info.host}:" \
                 f"{postgresql.info.port}/{postgresql.info.dbname}"
    db = Database(connection)
    db.create_tables()
    with db.get_session() as session:
        yield session
    Base.metadata.drop_all(db.engine)
