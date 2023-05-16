import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp.api.routers import api_router
from webapp.dependencies import init_tables

app = FastAPI(title="DevChat Webapp", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


def main():
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=False)


if __name__ == "__main__":
    init_tables()
    main()
