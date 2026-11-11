
# backend/app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables before importing database-dependent modules
load_dotenv()

from .database import init_pool, close_pool
from .routes import auth, student, staff, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()


app = FastAPI(
    title="CampusEats API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(student.router, prefix="/student", tags=["Student"])
app.include_router(staff.router, prefix="/staff", tags=["Staff"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "CampusEats API is running"}
