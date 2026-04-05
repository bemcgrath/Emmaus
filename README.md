# Emmaus

Open-source backend scaffold for Emmaus, a modular, agentic Bible study application. The design keeps Bible text, commentary, and AI logic decoupled so the project can stay MIT-licensed without bundling proprietary texts.

## Core Docs

- [Objective](docs/OBJECTIVE.md)
- [Product Blueprint](docs/PRODUCT_BLUEPRINT.md)
- [Roadmap](docs/ROADMAP.md)

## Goals

- Keep Bible text providers swappable.
- Allow users to register their own local-file or API-based text sources.
- Keep commentary integrations modular and optional.
- Expose clear API boundaries for text retrieval, study telemetry, and AI-driven study guidance.
- Support adaptive study flows based on recorded study patterns.

## Architecture

```text
emmaus/
  api/            FastAPI routes and request schemas
  core/           Settings and dependency bootstrap
  domain/         Shared models
  providers/      Text, commentary, and LLM provider interfaces
  repositories/   Persistence abstractions
  services/       App logic and adaptive agent behavior
data/             User-supplied or sample local text data
docs/             Product and objective references
tests/            API smoke tests
```

### Separation of concerns

- `BibleTextProvider` isolates passage retrieval from application logic.
- `CommentaryProvider` isolates commentary lookup from study orchestration.
- `LLMProvider` isolates AI vendor integrations from the adaptive study agent.
- `StudyService` records user activity and summarizes patterns.
- `AdaptiveStudyAgent` turns passage text plus study patterns into plans and questions.

## Included providers

- `LocalJsonBibleTextProvider`: reads from a user-supplied JSON file.
- `RemoteApiBibleTextProvider`: placeholder adapter for API-key-backed sources.
- `NotesPlaceholderCommentaryProvider`: placeholder for commentary plugins.
- `NullLLMProvider`: rule-based fallback until a real AI adapter is connected.

## Local text source format

A local source should look like this:

```json
{
  "name": "Sample KJV Excerpt",
  "copyright": "Public Domain",
  "books": {
    "John": {
      "3": {
        "16": "For God so loved the world..."
      }
    }
  }
}
```

## API endpoints

### Health

- `GET /health`

### Text sources

- `GET /v1/sources/text`
- `POST /v1/sources/text/local`
- `POST /v1/sources/text/api`

Example local registration:

```json
{
  "source_id": "my_public_domain_text",
  "name": "My Local Text",
  "file_path": "C:/path/to/text.json",
  "license_name": "Public Domain"
}
```

Example API registration:

```json
{
  "source_id": "my_api_text",
  "name": "My Bible API",
  "base_url": "https://api.example.com/bible",
  "api_key": "replace-me",
  "license_name": "User Supplied"
}
```

### Text lookup

- `POST /v1/texts/passage`

```json
{
  "source_id": "sample_local",
  "book": "John",
  "chapter": 3,
  "start_verse": 16,
  "end_verse": 17
}
```

### Commentary

- `GET /v1/commentary/sources`
- `POST /v1/commentary/lookup`

### Study telemetry

- `POST /v1/study/events`
- `GET /v1/study/patterns/{user_id}`

### Agentic study guidance

- `POST /v1/agent/session`

```json
{
  "user_id": "demo-user",
  "text_source_id": "sample_local",
  "commentary_source_id": "notes_placeholder",
  "llm_source_id": "local_rules",
  "reference": {
    "book": "Psalm",
    "chapter": 23,
    "start_verse": 1,
    "end_verse": 3
  }
}
```

The response includes:

- a session message
- adaptive study questions
- a suggested study plan
- a summary of recent study patterns

## Running locally

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
uvicorn emmaus.main:app --reload
```

## Open-source licensing posture

- The codebase is MIT licensed.
- No proprietary Bible texts or commentary are bundled.
- Users are expected to connect their own licensed or public-domain content through provider adapters.

## Suggested next steps

- Add persistent storage for study history and registered source configs.
- Implement a real HTTP adapter for API-backed Bible text providers.
- Add authenticated user accounts and per-user source ownership.
- Add richer plan generation with spaced repetition, mood signals, and action tracking.
- Add commentary provider packages for public-domain sources.
- Add an OpenAI-compatible or other LLM adapter behind the `LLMProvider` interface.


