# ESV Setup

This guide explains how to get an ESV API key from Crossway and use it in Emmaus.

## What you need to know

Emmaus does not bundle ESV text in the open-source repository.

Instead, ESV is connected at runtime through the official Crossway API. That means you need an API key from Crossway before Emmaus can fetch ESV passages.

## How to get an ESV API key

1. Go to [api.esv.org](https://api.esv.org/).
2. Sign in or create a Crossway account.
3. Register an application on the ESV API site.
4. Copy the API token Crossway gives you.

Crossway's terms and usage limits apply to that key and to any app that uses it.

## How to use the key in Emmaus

### Option 1. Paste it into the app

In the mobile source manager:

1. Open **Choose your Bible**.
2. Tap **Connect ESV**.
3. Paste your API key.
4. Save it.

Emmaus will register ESV as a connected source and let you make it your default Bible.

### Option 2. Configure it for a deployment

Set this environment variable:

```bash
EMMAUS_ESV_API_KEY=your-esv-api-key
```

When this is set, Emmaus will auto-register ESV at startup. If the default text source is still the starter Bible, Emmaus will treat ESV as the effective default source for that deployment.

## Notes

- You still need a Crossway-issued API key. Emmaus cannot create one for you.
- Keep the API key private.
- ESV usage remains subject to Crossway's API and copyright terms.
- If you want an open-source-safe fallback that can ship in the repo, use the included starter Bible or another public-domain source.
