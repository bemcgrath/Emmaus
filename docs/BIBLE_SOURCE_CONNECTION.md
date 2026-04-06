# Bible Source Connection

This document explains how Emmaus connects users to Bible text without bundling proprietary content.

## Principle

Emmaus separates Bible text retrieval from study logic.

The agent, personalization engine, and study flow never depend on one publisher or vendor format. They ask the text-source layer for a passage, and the provider returns a normalized passage payload.

## Supported connection paths

### 1. Local file source

A user can register a local JSON Bible file.

Endpoint:

- `POST /v1/sources/text/local`

Request body:

```json
{
  "source_id": "my_local_kjv",
  "name": "My Local KJV",
  "file_path": "C:\\path\\to\\bible.json",
  "license_name": "Public Domain"
}
```

This creates a local-file provider that Emmaus can call when it needs a passage.

### 2. Uploaded local JSON source`r`n`r`nA user can choose a JSON file from the mobile web client or any browser and upload it directly to Emmaus.`r`n`r`nEndpoint:`r`n`r`n- `POST /v1/sources/text/upload``r`n`r`nRequest body:`r`n`r`n```json`r`n{`r`n  "source_id": "my_uploaded_bible",`r`n  "name": "My Uploaded Bible",`r`n  "filename": "my_bible.json",`r`n  "file_content": "{...json contents...}",`r`n  "license_name": "Public Domain"`r`n}`r`n```

Emmaus stores the uploaded JSON under its data directory, registers it as a local provider, and makes it immediately available in the source list.

### 3. API-backed source

A user can register a remote Bible API adapter.

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

This creates a remote provider entry. The current implementation includes the adapter seam and placeholder response behavior so the app stays modular while users bring their own API-backed text.

## How the app uses a registered source

After a source is registered, the source appears in:

- `GET /v1/sources/text`

The user can then choose that source in one of two ways:

### Save it on the profile

Use:

- `PATCH /v1/users/{user_id}/preferences`

Set:

- `preferred_translation_source_id`

Example:

```json
{
  "preferred_translation_source_id": "my_local_kjv"
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
  "text_source_id": "my_local_kjv",
  "requested_minutes": 15
}
```

## Runtime flow

1. Emmaus receives a request for a passage or a study session.
2. The app resolves a `source_id` from the session request or the user's saved preference.
3. `TextSourceService` asks the provider registry for that source.
4. The provider returns a normalized passage object.
5. The agent and study services use that normalized passage without needing to know where the text came from.

## Important current note

The current mobile web client lets users do all three source tasks in-app: view connected sources, make one the default Bible, and add a new source through either JSON upload or API connection.

## Why this matters

This design lets Emmaus remain:

- open-source friendly
- modular
- permissive-license compatible
- able to support public-domain texts, licensed APIs, or user-supplied local files without coupling the app to one Bible vendor