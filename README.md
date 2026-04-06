# Emmaus

Emmaus is a mobile-first, agentic Bible study app built to help users deepen their relationship with Christ through adaptive, Scripture-centered guidance.

The app is designed around a personalized guide that helps users read, understand, apply, and return to Scripture in a way that fits their real habits, schedule, and spiritual needs. Bible text, commentary, and AI logic remain modular so the project can stay open-source and avoid bundling proprietary content.

## Current Status

Emmaus is currently in late `Phase 1` and early `Phase 2`.

That means:

- the MVP guide loop is real and usable end to end
- mobile-first study, action steps, reminders, and ESV-first setup are working
- personalization is already underway through mood, timing, memory, response evaluation, and adaptive session recommendations
- content depth is only lightly started through modular text-source work and ESV support

A practical way to think about the project right now:

- `Phase 1`: substantially complete
- `Phase 2`: actively in progress
- `Phase 3`: lightly started

The next priority is not foundational scaffolding anymore. It is making the guide feel more consistently pastoral, intelligent, and polished across real user flows.
## Core Docs

- [Objective](docs/OBJECTIVE.md)
- [Product Blueprint](docs/PRODUCT_BLUEPRINT.md)
- [Roadmap](docs/ROADMAP.md)
- [Bible Source Connection](docs/BIBLE_SOURCE_CONNECTION.md)
- [ESV Setup](docs/ESV_SETUP.md)
- [Licensed Translation Guide](docs/LICENSED_TRANSLATIONS.md)
- [Translation Provider Strategy](docs/TRANSLATION_PROVIDER_STRATEGY.md)
- [iPhone Prototyping Guide](docs/IPHONE_PROTOTYPING.md)

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
- ESV-first MVP: the first polished licensed-translation experience should be ESV, with partner-platform support for other licensed translations coming later.
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

## MVP Translation Focus

Emmaus should be fully usable for `ESV` in the MVP.

That means the MVP translation experience should prioritize:

- a smooth `Connect ESV` flow
- clear attribution and source visibility
- strong mobile-first ESV setup and selection UX
- the included starter Bible as the fallback when ESV is not connected

For now, `NIV` and `NASB` should remain documented licensing targets rather than active MVP commitments.

## Current API Surface

### Health

- `GET /health`

### Users and personalization

- `GET /v1/users/{user_id}/profile`
- `PATCH /v1/users/{user_id}/preferences`

### Text sources

- `GET /v1/sources/text`
- `POST /v1/sources/text/local`
- `POST /v1/sources/text/upload`
- `POST /v1/sources/text/api`
- `POST /v1/sources/text/esv`
- `GET /v1/sources/text/templates`

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

## Local LLM via Ollama

Emmaus now supports a real local LLM path through Ollama.

By default, Emmaus checks whether Ollama is reachable at `http://127.0.0.1:11434`. If it is, the existing `local_rules` provider automatically uses the configured Ollama model. If not, Emmaus falls back to the null provider so local development still works.

Default model:

- `phi3.5`

Helpful env vars:

- `EMMAUS_OLLAMA_BASE_URL`
- `EMMAUS_OLLAMA_MODEL`
- `EMMAUS_OLLAMA_CONNECT_TIMEOUT_SECONDS`
- `EMMAUS_OLLAMA_REQUEST_TIMEOUT_SECONDS`

Typical local setup:

```bash
ollama pull phi3.5
ollama serve
uvicorn emmaus.main:app --reload
```

Once Ollama is running locally, Emmaus will begin using it for session guidance through the `local_rules` provider without any route changes.
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
- a return-to-today�s-plan home screen that highlights the next best step
- session persistence that restores an in-progress study flow after refresh or return
- action-item follow-up that captures what happened when the user actually applied the session
- a session context block that explains why Emmaus chose the current focus, passage, and thread before the user starts responding
- a completion summary card that closes the session with what Emmaus noticed, what it will carry forward, and the action item to practice next
- a nudge preview plus delivery-plan surface that is ready to feed future mobile notifications

## How Bible connection works

Emmaus does not ship with proprietary Bible text. Instead, a user connects a Bible source once, and the app reads passages from that source through the text-provider layer.

The current connection flow is:

1. Register a source.
2. Save that source on the user profile or pass it when a session starts.
3. Emmaus resolves passages through the provider registry and keeps the rest of the app logic source-agnostic.

Current supported source types:

- Included starter Bible: Emmaus ships with a public-domain starter source so a user can begin immediately.
- ESV connection: connect ESV with a Crossway API key through POST /v1/sources/text/esv or the mobile source manager.
- Local file path: register a local JSON Bible file with POST /v1/sources/text/local.
- Uploaded local JSON: upload a Bible JSON file directly from the app with POST /v1/sources/text/upload.
- API-backed source: register a remote Bible API adapter with POST /v1/sources/text/api and an optional API key.

Once registered, the source appears in `GET /v1/sources/text`, and the user can reference it by `source_id` either as `preferred_translation_source_id` on the profile or `text_source_id` when starting a session.

The current web client now includes a mobile-friendly, translation-first Bible source manager. Users can choose a translation card first, then Emmaus routes them into the right setup path: included starter Bible, ESV API key, upload, or another provider.

If `EMMAUS_ESV_API_KEY` is configured for a deployment, Emmaus registers ESV automatically at startup and uses it as the effective default source unless another default is explicitly configured.

See [docs/BIBLE_SOURCE_CONNECTION.md](docs/BIBLE_SOURCE_CONNECTION.md) for the exact request flow and examples.

## Demo mode

Emmaus now includes a built-in demo mode for the mobile web client.

- The home screen includes scene buttons for `Live`, `First visit`, `Comprehension gap`, `In progress`, `Overdue action`, and `Scheduled nudge`.
- Demo scenes are read-only and never write to the live database.
- You can also open a seeded state directly with `?demo=first_visit`, `?demo=comprehension_gap`, `?demo=in_progress`, `?demo=overdue_action`, or `?demo=scheduled_nudge`.
- Switch back to `Live` anytime to use the real API-backed experience.

## Open-source licensing posture

- The codebase is MIT licensed.
- No proprietary Bible texts or commentary are bundled.
- Users are expected to connect their own licensed or public-domain content through provider adapters.


