from fastapi import FastAPI
from .entities import organization

app = FastAPI()

app.include_router(organization.router, prefix="/organizations", tags=["organizations"])
