from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from emmaus.api.routes import agent, commentary, engagement, health, study, text_sources, texts, users
from emmaus.core.bootstrap import build_container


container = build_container()
web_dir = Path(__file__).resolve().parent / "web"
static_dir = web_dir / "static"

app = FastAPI(
    title="Emmaus API",
    version="0.1.0",
    summary="Open-source backend for adaptive Bible study with pluggable text and AI sources in Emmaus.",
)

app.state.container = container

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(web_dir / "index.html")


app.include_router(health.router)
app.include_router(users.router, prefix="/v1")
app.include_router(text_sources.router, prefix="/v1")
app.include_router(texts.router, prefix="/v1")
app.include_router(commentary.router, prefix="/v1")
app.include_router(study.router, prefix="/v1")
app.include_router(engagement.router, prefix="/v1")
app.include_router(agent.router, prefix="/v1")
