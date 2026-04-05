from fastapi import FastAPI

from emmaus.api.routes import agent, commentary, health, study, text_sources, texts
from emmaus.core.bootstrap import build_container


container = build_container()

app = FastAPI(
    title="Emmaus API",
    version="0.1.0",
    summary="Open-source backend for adaptive Bible study with pluggable text and AI sources in Emmaus.",
)

app.state.container = container

app.include_router(health.router)
app.include_router(text_sources.router, prefix="/v1")
app.include_router(texts.router, prefix="/v1")
app.include_router(commentary.router, prefix="/v1")
app.include_router(study.router, prefix="/v1")
app.include_router(agent.router, prefix="/v1")

