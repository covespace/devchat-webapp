from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from webapp.api.routers import router

app = FastAPI(title="DevChat Webapp", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
