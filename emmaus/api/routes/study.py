from fastapi import APIRouter, Depends

from emmaus.api.deps import get_container
from emmaus.api.schemas import StudyEventRequest
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/study", tags=["study"])


@router.post("/events", status_code=201)
def record_event(payload: StudyEventRequest, container: Container = Depends(get_container)):
    return container.study_service.record_event(payload.to_model())


@router.get("/patterns/{user_id}")
def get_patterns(user_id: str, container: Container = Depends(get_container)):
    return container.study_service.summarize_patterns(user_id)
