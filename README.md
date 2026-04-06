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

### Agentic session lifecycle and nudges

- `GET /v1/agent/recommendations/{user_id}`
- `GET /v1/agent/session/active/{user_id}`
- `POST /v1/agent/nudges/preview`
- `POST /v1/agent/nudges/plan`
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

- onboarding that captures guide mode, study rhythm, preferred days, timing windows, and nudge tone
- a return-to-today’s-plan home screen that highlights the next best step
- session persistence that restores an in-progress study flow after refresh or return
- action-item follow-up that captures what happened when the user actually applied the session
- a nudge preview plus delivery-plan surface that is ready to feed future mobile notifications

## Demo mode

Emmaus now includes a built-in demo mode for the mobile web client.

- The home screen includes scene buttons for `Live`, `First visit`, `In progress`, `Overdue action`, and `Scheduled nudge`.
- Demo scenes are read-only and never write to the live database.
- You can also open a seeded state directly with `?demo=first_visit`, `?demo=in_progress`, `?demo=overdue_action`, or `?demo=scheduled_nudge`.
- Switch back to `Live` anytime to use the real API-backed experience.

## Open-source licensing posture

- The codebase is MIT licensed.
- No proprietary Bible texts or commentary are bundled.
- Users are expected to connect their own licensed or public-domain content through provider adapters.

