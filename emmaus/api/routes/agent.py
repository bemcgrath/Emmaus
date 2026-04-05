from fastapi import APIRouter, Depends

from emmaus.api.deps import get_container
from emmaus.api.schemas import AgentSessionRequest
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/session")
def build_agent_session(payload: AgentSessionRequest, container: Container = Depends(get_container)):
    return container.agent_service.build_session(
        user_id=payload.user_id,
        reference=payload.reference,
        text_source_id=payload.text_source_id,
        commentary_source_id=payload.commentary_source_id,
        llm_source_id=payload.llm_source_id,
    )
