from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.domain import Domain
from app.models.info_item import InfoItem, InfoItemDomain
from app.schemas import AlertUpsertIn, InfoItemDraftIn, InfoItemOut, InfoItemPublishIn

router = APIRouter(tags=["info-items"])


DRAFT_STATUSES = {"draft", "ai_suggested"}


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
        draft_data=item.draft_data or {},
        alert_status=item.alert_status,
        alert_source=item.alert_source,
        alert_manual_override=item.alert_manual_override,
        alert_title=item.alert_title,
        alert_body=item.alert_body,
        alert_reviewer_comment=item.alert_reviewer_comment,
        alert_dismiss_reason=item.alert_dismiss_reason,
        alert_color=item.alert_color,
        alert_expires_at=item.alert_expires_at,
    )


def _apply_alert_payload(item: InfoItem, alert: AlertUpsertIn | None) -> None:
    if not alert or not alert.enabled:
        item.alert_status = "dismissed" if alert else None
        item.alert_source = "manual" if alert else None
        item.alert_manual_override = bool(alert)
        item.alert_title = None
        item.alert_body = None
        item.alert_reviewer_comment = None
        item.alert_color = None
        item.alert_expires_at = None
        item.alert_dismiss_reason = alert.dismiss_reason if alert else None
        return

    if not alert.alert_title:
        raise HTTPException(status_code=400, detail="alert_title is required when alert is enabled")
    if not alert.alert_body:
        raise HTTPException(status_code=400, detail="alert_body is required when alert is enabled")
    if not alert.reviewer_comment:
        raise HTTPException(status_code=400, detail="reviewer_comment is required when alert is enabled")

    item.alert_status = "active"
    item.alert_source = "manual"
    item.alert_manual_override = True
    item.alert_title = alert.alert_title
    item.alert_body = alert.alert_body
    item.alert_reviewer_comment = alert.reviewer_comment
    item.alert_color = alert.alert_color or "orange"
    item.alert_expires_at = alert.expires_at
    item.alert_dismiss_reason = None


def _validate_domain_ids(db: Session, domain_ids: list[str]) -> list[str]:
    if not domain_ids:
        raise HTTPException(status_code=400, detail="domain_ids is required")
    unique_ids = list(dict.fromkeys(domain_ids))
    existing_domain_ids = set(
        db.scalars(select(Domain.id).where(Domain.id.in_(unique_ids))).all()
    )
    if len(existing_domain_ids) != len(unique_ids):
        raise HTTPException(status_code=400, detail="some domain_ids do not exist")
    return unique_ids


def _replace_domains(db: Session, item: InfoItem, domain_ids: list[str]) -> None:
    db.query(InfoItemDomain).filter(InfoItemDomain.info_item_id == item.id).delete(synchronize_session=False)
    for idx, domain_id in enumerate(domain_ids):
        db.add(
            InfoItemDomain(
                info_item_id=item.id,
                domain_id=domain_id,
                is_primary=(idx == 0),
            )
        )


def _apply_upsert_fields(item: InfoItem, payload: InfoItemDraftIn | InfoItemPublishIn) -> None:
    item.title = payload.title
    item.content = payload.content
    item.source_url = payload.source_url
    item.published_at = payload.published_at
    item.importance_score = payload.importance_score
    item.is_new_tech = payload.is_new_tech
    item.comment = payload.comment
    item.source_types = payload.source_types
    item.info_types = payload.info_types
    item.tags = payload.tags
    item.classification = payload.classification


@router.get("/info-items", response_model=list[InfoItemOut])
def get_info_items(
    status_filter: str = Query("published", alias="status"),
    db: Session = Depends(get_db),
) -> list[InfoItemOut]:
    statuses = [s.strip() for s in status_filter.split(",") if s.strip()]
    if not statuses:
        statuses = ["published"]

    stmt: Select[tuple[InfoItem]] = (
        select(InfoItem)
        .options(selectinload(InfoItem.domains))
        .where(InfoItem.status.in_(statuses))
        .order_by(InfoItem.published_at.desc().nullslast(), InfoItem.created_at.desc())
    )

    items = db.scalars(stmt).all()
    return [_to_info_item_out(item) for item in items]


@router.get("/info-items/drafts", response_model=list[InfoItemOut])
def get_drafts(db: Session = Depends(get_db)) -> list[InfoItemOut]:
    stmt: Select[tuple[InfoItem]] = (
        select(InfoItem)
        .options(selectinload(InfoItem.domains))
        .where(InfoItem.status.in_(DRAFT_STATUSES))
        .order_by(InfoItem.updated_at.desc())
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


@router.get("/info-items/{item_id}/draft", response_model=InfoItemOut)
def get_draft(item_id: UUID, db: Session = Depends(get_db)) -> InfoItemOut:
    stmt: Select[tuple[InfoItem]] = (
        select(InfoItem)
        .options(selectinload(InfoItem.domains))
        .where(InfoItem.id == item_id)
    )
    item = db.scalars(stmt).first()
    if not item or item.status not in DRAFT_STATUSES:
        raise HTTPException(status_code=404, detail="draft not found")
    return _to_info_item_out(item)


@router.delete("/info-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_info_item(item_id: UUID, db: Session = Depends(get_db)) -> Response:
    item = db.get(InfoItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="info item not found")
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/info-items/draft", response_model=InfoItemOut, status_code=status.HTTP_201_CREATED)
def create_draft(payload: InfoItemDraftIn, db: Session = Depends(get_db)) -> InfoItemOut:
    if payload.status not in DRAFT_STATUSES:
        raise HTTPException(status_code=400, detail="draft status must be draft or ai_suggested")
    domain_ids = _validate_domain_ids(db, payload.domain_ids)

    item = InfoItem(status=payload.status)
    _apply_upsert_fields(item, payload)
    item.draft_data = payload.draft_data or {}
    _apply_alert_payload(item, payload.alert)

    db.add(item)
    db.flush()
    _replace_domains(db, item, domain_ids)
    db.commit()
    db.refresh(item)
    return _to_info_item_out(item)


@router.put("/info-items/{item_id}/draft", response_model=InfoItemOut)
def update_draft(item_id: UUID, payload: InfoItemDraftIn, db: Session = Depends(get_db)) -> InfoItemOut:
    if payload.status not in DRAFT_STATUSES:
        raise HTTPException(status_code=400, detail="draft status must be draft or ai_suggested")
    stmt: Select[tuple[InfoItem]] = (
        select(InfoItem)
        .options(selectinload(InfoItem.domains))
        .where(InfoItem.id == item_id)
    )
    item = db.scalars(stmt).first()
    if not item or item.status not in DRAFT_STATUSES:
        raise HTTPException(status_code=404, detail="draft not found")

    domain_ids = _validate_domain_ids(db, payload.domain_ids)
    _apply_upsert_fields(item, payload)
    item.status = payload.status
    item.draft_data = payload.draft_data or {}
    _apply_alert_payload(item, payload.alert)
    _replace_domains(db, item, domain_ids)

    db.commit()
    db.refresh(item)
    return _to_info_item_out(item)


@router.post(
    "/info-items/publish",
    response_model=InfoItemOut,
    status_code=status.HTTP_201_CREATED,
)
def publish_info_item(payload: InfoItemPublishIn, db: Session = Depends(get_db)) -> InfoItemOut:
    domain_ids = _validate_domain_ids(db, payload.domain_ids)

    item: InfoItem | None = None
    if payload.draft_id:
        stmt: Select[tuple[InfoItem]] = (
            select(InfoItem)
            .options(selectinload(InfoItem.domains))
            .where(InfoItem.id == payload.draft_id)
        )
        item = db.scalars(stmt).first()
        if not item or item.status not in DRAFT_STATUSES:
            raise HTTPException(status_code=404, detail="draft not found")

    if item is None:
        item = InfoItem(status="published")
        db.add(item)

    _apply_upsert_fields(item, payload)
    # For non-draft publish, required fields must be assigned before first flush/insert.
    if payload.draft_id is None:
        db.flush()
    item.status = "published"
    item.draft_data = {}
    _apply_alert_payload(item, payload.alert)
    _replace_domains(db, item, domain_ids)

    db.commit()
    db.refresh(item)

    return _to_info_item_out(item)


@router.patch("/info-items/{item_id}/alert", response_model=InfoItemOut)
def upsert_info_item_alert(
    item_id: UUID,
    payload: AlertUpsertIn,
    db: Session = Depends(get_db),
) -> InfoItemOut:
    stmt: Select[tuple[InfoItem]] = (
        select(InfoItem)
        .options(selectinload(InfoItem.domains))
        .where(InfoItem.id == item_id)
    )
    item = db.scalars(stmt).first()
    if not item:
        raise HTTPException(status_code=404, detail="info item not found")

    _apply_alert_payload(item, payload)
    db.commit()
    db.refresh(item)
    return _to_info_item_out(item)
