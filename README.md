# Emmaus

Emmaus is a mobile-first, agentic Bible study app built to help users deepen their relationship with Christ through adaptive, Scripture-centered guidance.

The app is designed around a personalized guide that helps users read, understand, apply, and return to Scripture in a way that fits their real habits, schedule, and spiritual needs. Bible text, commentary, and AI logic remain modular so the project can stay open-source and avoid bundling proprietary content.

## Core Docs

- [Objective](docs/OBJECTIVE.md)
- [Product Blueprint](docs/PRODUCT_BLUEPRINT.md)
- [Roadmap](docs/ROADMAP.md)

## Core Product Direction

Emmaus is built around one core behavior:

- the guide gauges comprehension
- the guide identifies gaps in understanding or application
- the guide adapts future study plans to address those gaps
- the guide ends each session with a practical action or reflection

This adaptive cycle of testing, tailoring, and applying is the center of the product.

## Product Principles

- Christ-centered: the purpose of the app is to help users grow in relationship with Christ through Scripture.
- Scripture-first: the Bible text remains primary, and the guide serves the text rather than replacing it.
- Personalized: study plans, prompts, and next steps adapt to the user over time.
- Action-oriented: every session should move toward obedience, reflection, prayer, or discussion.
- Mobile-first: the experience should feel natural, concise, and intuitive on a smartphone.
- Modular: Bible text sources, commentary sources, and AI providers remain decoupled.
- Open-source friendly: the architecture should remain compatible with permissive licensing like MIT.

## Mobile-First Product Expectations

Emmaus should be designed first for phones, then expanded outward.

That means:

- concise prompts and readable passage chunks
- simple navigation with minimal taps between reading and response
- agent messages that fit naturally in a mobile conversation flow
- session entry points built around short available time windows
- action items, streaks, and follow-up cues that are easy to review on a small screen

## Architecture

```text
emmaus/
  api/            FastAPI routes and request schemas
  core/           Settings and dependency bootstrap
  domain/         Shared models
  providers/      Text, commentary, and LLM provider interfaces
  repositories/   Persistence abstractions
  services/       App logic and adaptive agent behavior
  web/            Mobile-first web client served by FastAPI
data/             User-supplied or sample local text data
docs/             Product and objective references
tests/            API and frontend smoke tests
```

### Separation of concerns

- `BibleTextProvider` isolates passage retrieval from application logic.
- `CommentaryProvider` isolates commentary lookup from study orchestration.
- `LLMProvider` isolates AI vendor integrations from the adaptive study agent.
- `StudyService` records user activity, profiles, sessions, and action items.
- `AdaptiveStudyAgent` runs the adaptive cycle of session planning, questioning, and application.

## Included providers

- `LocalJsonBibleTextProvider`: reads from a user-supplied JSON file.
- `RemoteApiBibleTextProvider`: placeholder adapter for API-key-backed sources.
- `NotesPlaceholderCommentaryProvider`: placeholder for commentary plugins.
- `NullLLMProvider`: rule-based fallback until a real AI adapter is connected.

## Current API Surface

### Health

- `GET /health`

### Users and personalization

- `GET /v1/users/{user_id}/profile`
- `PATCH /v1/users/{user_id}/preferences`

### Text sources

- `GET /v1/sources/text`
- `POST /v1/sources/text/local`
- `POST /v1/sources/text/api`

### Text lookup

- `POST /v1/texts/passage`

### Commentary

- `GET /v1/commentary/sources`
- `POST /v1/commentary/lookup`

### Study and action items

- `POST /v1/study/events`
- `GET /v1/study/patterns/{user_id}`
- `POST /v1/study/mood`
- `GET /v1/study/mood/{user_id}`
- `GET /v1/study/action-items/{user_id}`
- `POST /v1/study/action-items`
- `POST /v1/study/action-items/{action_item_id}/complete`

### Agentic session lifecycle

- `GET /v1/agent/recommendations/{user_id}`
- `GET /v1/agent/session/active/{user_id}`
- `POST /v1/agent/nudges/preview`
- `POST /v1/agent/session`
- `POST /v1/agent/session/start`
- `POST /v1/agent/session/respond`
- `POST /v1/agent/session/complete`

### Engagement

- `GET /v1/engagement/streaks/{user_id}`

## Running locally

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
uvicorn emmaus.main:app --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) to use the mobile-first Emmaus web client.

## Mobile-first frontend surface

Emmaus now includes a lightweight mobile web client served directly from the FastAPI app at `/`.

The current frontend emphasizes:

- onboarding for first-time users so the guide starts with basic context
- a return-to-today’s-plan home screen that highlights the next best step
- session persistence that restores an in-progress study flow after refresh or return
- a guided session screen for passage reading, question response, and completion
- an action-item view for follow-through after study
- a nudge preview screen that shows timing-aware re-engagement guidance

This keeps the interaction model close to the backend while the product surface is still taking shape.

## Open-source licensing posture

- The codebase is MIT licensed.
- No proprietary Bible texts or commentary are bundled.
- Users are expected to connect their own licensed or public-domain content through provider adapters.
