from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.config import settings
from backend.database import init_db
from backend.routers import auth, sync, applications, dashboard

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="HireFlow", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
