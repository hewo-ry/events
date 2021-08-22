from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from core.auth import router as auth_router

from core.database.schemas import Meta

from config import settings

app = FastAPI(root_path=settings.ROOT_PATH, title=settings.SERVER_NAME)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Routers
app.include_router(auth_router)


@app.get("/meta", response_model=Meta)
def meta():
    return {"version": settings.VERSION, "build": settings.BUILD}
