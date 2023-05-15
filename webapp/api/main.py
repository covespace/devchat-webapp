import os
from fastapi import FastAPI
from sqlalchemy.orm import Session
from webapp.model.database import Database
from webapp.api.entities import organization

# Replace this with your actual database URL
DATABASE_URL = os.environ["DATABASE_URL"]

database = Database(DATABASE_URL)
database.create_tables()


def get_db() -> Session:
    with database.get_session() as session:
        yield session


app = FastAPI()

app.include_router(organization.router, prefix="/organizations", tags=["organizations"])
