import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Set the default database URL for development
DATABASE_URL = "sqlite:///devchat-webapp.db"

# Override the database URL with the environment variable, if available
if os.environ.get("DATABASE_URL"):
    DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def create_tables():
    """Create the tables in the database."""
    Base.metadata.create_all(engine)


def init_db():
    """Initialize the database with some sample data."""


if __name__ == "__main__":
    create_tables()
    init_db()
