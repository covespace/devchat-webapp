from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp import logger
from webapp.api.routers import api_router
from webapp.dependencies import init_tables

logger.setup_logger()

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
    """
    When testing locally, you can set the DATABASE_URL environment variable to connect to a local database.
    For example: launch the database container with the following command:
    `docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres:latest`
    
    Then set the DATABASE_URL environment variable:
    1. In container-based environments:
        1. Get the IP address of the database container:
        `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' some-postgres`
        2. Set the DATABASE_URL environment variable:`
        `docker run -d -p 8000:8000 --name my-webapp \
           -e DATABASE_URL="postgresql://postgres:mysecretpassword@<POSTGRES_IP_ADDRESS>:5432/postgres" your-image-name`
    2. In non-container-based environments:
        1. Set the DATABASE_URL environment variable:
        `export DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:5432/postgres"`
        or in Python:
        `os.environ["DATABASE_URL"] = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"`
        
    NOTICE: The IP address with PG is localhost if you are running webapp locally.
    """
    init_tables()
    main()
