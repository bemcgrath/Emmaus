# Bible Source Connection

This document explains how Emmaus connects users to Bible text without bundling proprietary content in the repository.

## Principle

Emmaus separates Bible text retrieval from study logic.

The agent, personalization engine, and study flow never depend on one publisher or vendor format. They ask the text-source layer for a passage, and the provider returns a normalized passage payload.

## Default behavior

Emmaus includes a starter Bible so a new user can begin immediately.

That starter source is safe for the open-source repo because it uses public-domain text. Proprietary sources such as ESV are connected at runtime instead of being bundled into the codebase.

## Supported connection paths

### 1. Included starter Bible

Emmaus registers a starter source at boot when the bundled sample data is present.

This gives new users a one-tap Bible choice even before they connect anything else.

### 2. ESV through the official API

A user can connect ESV with a Crossway API key.

Endpoint:

- `POST /v1/sources/text/esv`

Request body:

```json
{
  "api_key": "your-esv-api-key",
  "source_id": "esv",
  "name": "ESV"
}
```

Emmaus registers ESV as a runtime API-backed source and can make it the user's default Bible immediately after connection.

If `EMMAUS_ESV_API_KEY` is set for a deployment, Emmaus also auto-registers ESV at startup.

### 3. Local file source

A user can register a local JSON Bible file.

Endpoint:

- `POST /v1/sources/text/local`

Request body:

```json
{
  "source_id": "my_local_kjv",
  "name": "My Local KJV",
  "file_path": "C:\path\to\bible.json",
  "license_name": "Public Domain"
}
```

### 4. Uploaded local JSON source

A user can choose a JSON file from the mobile web client or any browser and upload it directly to Emmaus.

Endpoint:

- `POST /v1/sources/text/upload`

Request body:

```json
{
  "source_id": "my_uploaded_bible",
  "name": "My Uploaded Bible",
  "filename": "my_bible.json",
  "file_content": "{...json contents...}",
  "license_name": "Public Domain"
}
```

Emmaus stores the uploaded JSON under its data directory, registers it as a local provider, and makes it immediately available in the source list.

### 5. Generic API-backed source

A user can register another remote Bible API adapter.

Endpoint:

- `POST /v1/sources/text/api`

Request body:

```json
{
  "source_id": "my_api_source",
  "name": "My Bible API",
  "base_url": "https://example.com/bible",
  "api_key": "user-secret-key",
  "license_name": "User Supplied"
}
```

This keeps Emmaus modular even when the user brings a licensed or custom text API.

## How the app uses a registered source

After a source is registered, it appears in:

- `GET /v1/sources/text`

The user can then choose that source in one of two ways.

### Save it on the profile

Use:

- `PATCH /v1/users/{user_id}/preferences`

Set:

- `preferred_translation_source_id`

Example:

```json
{
  "preferred_translation_source_id": "esv"
}
```

### Pass it on a specific session

Use:

- `POST /v1/agent/session/start`

Set:

- `text_source_id`

Example:

```json
{
  "user_id": "demo-user",
  "text_source_id": "esv",
  "requested_minutes": 15
}
```

## Runtime flow

1. Emmaus receives a request for a passage or a study session.
2. The app resolves a `source_id` from the session request, the user's saved preference, or the configured default source.
3. `TextSourceService` asks the provider registry for that source.
4. The provider returns a normalized passage object.
5. The agent and study services use that normalized passage without needing to know where the text came from.

## Mobile UX note

The mobile web client now supports a translation-first chooser, so the setup starts with the Bible the user wants rather than with provider jargon. Emmaus currently guides users into these paths:

- Included Starter Bible: one tap and begin
- ESV: connect with an API key
- WEB, KJV, ASV: upload a JSON file from this device
- Other licensed translations: connect a provider/API

Emmaus also exposes `GET /v1/sources/text/templates` so clients can render these translation setup options consistently.

## Why this matters

This design lets Emmaus remain:

- open-source friendly
- modular
- permissive-license compatible
- able to support public-domain texts, licensed APIs, or user-supplied local files without coupling the app to one Bible vendor
