from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.data_loader import load_json

router = APIRouter(tags=["info-items"])


@router.get("/info-items")
def get_info_items() -> list[dict]:
    try:
        items = load_json("info_items.json")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail="info_items.json not found") from exc

    if not isinstance(items, list):
        raise HTTPException(status_code=500, detail="info_items.json is invalid")

    return items
