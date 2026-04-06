from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from emmaus.api.deps import get_container
from emmaus.api.schemas import CompleteActionItemRequest, CreateActionItemRequest, MoodCheckInRequest, StudyEventRequest
from emmaus.core.bootstrap import Container
from emmaus.domain.models import ActionItem


router = APIRouter(prefix="/study", tags=["study"])


@router.post("/events", status_code=201)
def record_event(payload: StudyEventRequest, container: Container = Depends(get_container)):
    return container.study_service.record_event(payload.to_model())


@router.get("/patterns/{user_id}")
def get_patterns(user_id: str, container: Container = Depends(get_container)):
    return container.study_service.summarize_patterns(user_id)


@router.post("/mood", status_code=201)
def record_mood_checkin(payload: MoodCheckInRequest, container: Container = Depends(get_container)):
    return container.study_service.record_mood_checkin(payload.to_model())


@router.get("/mood/{user_id}")
def get_latest_mood(user_id: str, container: Container = Depends(get_container)):
    return container.study_service.get_latest_mood_checkin(user_id)


@router.get("/action-items/{user_id}")
def list_action_items(user_id: str, status: str | None = None, container: Container = Depends(get_container)):
    return {"items": container.study_service.list_action_items(user_id, status)}


@router.post("/action-items", status_code=201)
def create_action_item(payload: CreateActionItemRequest, container: Container = Depends(get_container)):
    action_item = ActionItem(
        action_item_id=str(uuid4()),
        user_id=payload.user_id,
        session_id=payload.session_id,
        title=payload.title,
        detail=payload.detail,
    )
    return container.study_service.create_action_item(action_item)


@router.post("/action-items/{action_item_id}/complete")
def complete_action_item(
    action_item_id: str,
    payload: CompleteActionItemRequest,
    container: Container = Depends(get_container),
):
    try:
        return container.study_service.complete_action_item(
            action_item_id,
            payload.user_id,
            follow_up_note=payload.follow_up_note,
            follow_up_outcome=payload.follow_up_outcome,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
