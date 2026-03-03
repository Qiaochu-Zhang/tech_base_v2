from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.domain import Domain
from app.models.info_item import InfoItem, InfoItemDomain
from app.schemas import InfoItemOut, InfoItemPublishIn

router = APIRouter(tags=["info-items"])


def _to_info_item_out(item: InfoItem) -> InfoItemOut:
    return InfoItemOut(
        id=item.id,
        title=item.title,
        content=item.content,
        source_url=item.source_url,
        published_at=item.published_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
        status=item.status,
        importance_score=item.importance_score,
        is_new_tech=item.is_new_tech,
        comment=item.comment,
        source_types=item.source_types or [],
        info_types=item.info_types or [],
        tags=item.tags or [],
        domain_ids=[rel.domain_id for rel in item.domains],
        classification=item.classification,
    )


@router.get("/info-items", response_model=list[InfoItemOut])
def get_info_items(
    status_filter: str = Query("published", alias="status"),
    db: Session = Depends(get_db),
) -> list[InfoItemOut]:
    stmt: Select[tuple[InfoItem]] = (
        select(InfoItem)
        .options(selectinload(InfoItem.domains))
        .where(InfoItem.status == status_filter)
        .order_by(InfoItem.published_at.desc().nullslast(), InfoItem.created_at.desc())
    )

    items = db.scalars(stmt).all()
    return [_to_info_item_out(item) for item in items]


@router.get("/info-items/{item_id}", response_model=InfoItemOut)
def get_info_item(item_id: UUID, db: Session = Depends(get_db)) -> InfoItemOut:
    stmt: Select[tuple[InfoItem]] = (
        select(InfoItem)
        .options(selectinload(InfoItem.domains))
        .where(InfoItem.id == item_id)
    )
    item = db.scalars(stmt).first()
    if not item:
        raise HTTPException(status_code=404, detail="info item not found")
    return _to_info_item_out(item)


@router.delete("/info-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_info_item(item_id: UUID, db: Session = Depends(get_db)) -> Response:
    item = db.get(InfoItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="info item not found")
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/info-items/publish",
    response_model=InfoItemOut,
    status_code=status.HTTP_201_CREATED,
)
def publish_info_item(payload: InfoItemPublishIn, db: Session = Depends(get_db)) -> InfoItemOut:
    if not payload.domain_ids:
        raise HTTPException(status_code=400, detail="domain_ids is required")
    domain_ids = list(dict.fromkeys(payload.domain_ids))
    existing_domain_ids = set(
        db.scalars(select(Domain.id).where(Domain.id.in_(domain_ids))).all()
    )
    if len(existing_domain_ids) != len(domain_ids):
        raise HTTPException(status_code=400, detail="some domain_ids do not exist")

    item = InfoItem(
        title=payload.title,
        content=payload.content,
        source_url=payload.source_url,
        published_at=payload.published_at,
        status="published",
        importance_score=payload.importance_score,
        is_new_tech=payload.is_new_tech,
        comment=payload.comment,
        source_types=payload.source_types,
        info_types=payload.info_types,
        tags=payload.tags,
        classification=payload.classification,
    )
    db.add(item)
    db.flush()

    for idx, domain_id in enumerate(domain_ids):
        db.add(
            InfoItemDomain(
                info_item_id=item.id,
                domain_id=domain_id,
                is_primary=(idx == 0),
            )
        )

    db.commit()
    db.refresh(item)

    return _to_info_item_out(item)
