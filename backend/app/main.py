from fastapi import FastAPI

from app.routers import domains, health, info_items

app = FastAPI(title="Tech Intel API", version="0.1.0")

app.include_router(health.router, prefix="/api")
app.include_router(domains.router, prefix="/api")
app.include_router(info_items.router, prefix="/api")
