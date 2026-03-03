import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import SessionLocal
from app.routers import domains, health, info_items
from app.services.bootstrap import seed_domains_if_empty

app = FastAPI(title="Tech Intel API", version="0.2.0")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(domains.router, prefix="/api")
app.include_router(info_items.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    try:
        db = SessionLocal()
        try:
            seed_domains_if_empty(db)
        finally:
            db.close()
    except Exception as exc:  # pragma: no cover
        logger.warning("database bootstrap skipped: %s", exc)
