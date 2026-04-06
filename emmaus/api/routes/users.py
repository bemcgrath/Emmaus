from fastapi import APIRouter, Depends

from emmaus.api.deps import get_container
from emmaus.api.schemas import UpdateUserPreferencesRequest
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/profile")
def get_user_profile(user_id: str, container: Container = Depends(get_container)):
    return container.study_service.get_profile(user_id)


@router.get("/{user_id}/memory")
def get_user_memory(user_id: str, container: Container = Depends(get_container)):
    return container.study_service.summarize_spiritual_memory(user_id)


@router.patch("/{user_id}/preferences")
def update_user_preferences(
    user_id: str,
    payload: UpdateUserPreferencesRequest,
    container: Container = Depends(get_container),
):
    return container.study_service.update_preferences(
        user_id=user_id,
        updates=payload.preference_updates(),
        display_name=payload.display_name,
    )
