from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Domain
from app.services.data_loader import load_json


def seed_domains_if_empty(db: Session) -> None:
    exists = db.scalar(select(Domain.id).limit(1))
    if exists:
        return

    raw_domains = load_json("domains.json")
    if not isinstance(raw_domains, list):
        return

    for row in raw_domains:
        if not isinstance(row, dict):
            continue
        if not row.get("id") or not row.get("name"):
            continue
        db.add(
            Domain(
                id=row["id"],
                name=row["name"],
                parent_id=row.get("parent_id"),
            )
        )
    db.commit()
