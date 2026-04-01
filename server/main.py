import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import auth, employees, tariffs, payments, photos

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

app = FastAPI(
    title="Opus API",
    description="API для платформы Opus — поиск сотрудников",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(tariffs.router)
app.include_router(payments.router)
app.include_router(photos.router)


@app.get("/")
async def root():
    return {"message": "Opus API v1.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
