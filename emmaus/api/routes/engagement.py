from fastapi import APIRouter, Depends

from emmaus.api.deps import get_container
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/engagement", tags=["engagement"])


@router.get("/streaks/{user_id}")
def get_streaks(user_id: str, container: Container = Depends(get_container)):
    return container.study_service.get_engagement_summary(user_id)
