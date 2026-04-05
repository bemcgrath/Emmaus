from fastapi import APIRouter, Depends, HTTPException

from emmaus.api.deps import get_container
from emmaus.api.schemas import AgentSessionRequest, CompleteAgentSessionRequest, RespondAgentSessionRequest, StartAgentSessionRequest
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


@router.post("/session/start")
def start_agent_session(payload: StartAgentSessionRequest, container: Container = Depends(get_container)):
    return container.agent_service.start_session(
        user_id=payload.user_id,
        display_name=payload.display_name,
        reference=payload.reference,
        text_source_id=payload.text_source_id,
        commentary_source_id=payload.commentary_source_id,
        llm_source_id=payload.llm_source_id,
        entry_point=payload.entry_point,
        requested_minutes=payload.requested_minutes,
        guide_mode=payload.guide_mode,
    )


@router.post("/session/respond")
def respond_agent_session(payload: RespondAgentSessionRequest, container: Container = Depends(get_container)):
    try:
        return container.agent_service.respond_to_session(
            session_id=payload.session_id,
            user_id=payload.user_id,
            response_text=payload.response_text,
            engagement_score=payload.engagement_score,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/session/complete")
def complete_agent_session(payload: CompleteAgentSessionRequest, container: Container = Depends(get_container)):
    try:
        return container.agent_service.complete_session(
            session_id=payload.session_id,
            user_id=payload.user_id,
            summary_notes=payload.summary_notes,
            action_item_title=payload.action_item_title,
            action_item_detail=payload.action_item_detail,
            engagement_score=payload.engagement_score,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
