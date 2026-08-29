from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import close_mongodb, connect_to_mongodb
from app.routers import auth, items

@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongodb()
    yield
    await close_mongodb()

app = FastAPI(title="WarrantyWise API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.frontend_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(items.router)

@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
