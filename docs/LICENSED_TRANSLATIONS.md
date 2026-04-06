# Licensed Translation Connection Guide

This guide documents the connection process Emmaus should follow for the three licensed translations we want to prioritize:

- ESV
- NIV
- NASB

The goal is to keep the user experience consistent while respecting each publisher's licensing and technical requirements.

## Summary

| Translation | Publisher / Rights Holder | Self-serve API path | Written permission likely needed for Emmaus? | Current Emmaus status |
| --- | --- | --- | --- | --- |
| ESV | Crossway | Yes | Not always, if Emmaus stays within Crossway's API conditions | Supported now through a dedicated ESV connection |
| NIV | Biblica | Indirect partner path only | Yes, likely, because Emmaus includes AI features | Not yet supported; requires licensing work first |
| NASB | The Lockman Foundation | No public self-serve API documented | Yes, likely, for app-scale integration beyond limited quoting | Not yet supported; requires permission path first |

## 1. ESV

### Official path

Crossway provides the official ESV API.

Process:

1. Create or sign in to an account at `api.esv.org`.
2. Register an API application.
3. Receive an API key.
4. Use that key in Emmaus through the ESV connection flow.

### What Emmaus can do

Emmaus can support ESV through a dedicated runtime API provider as long as the deployment stays within Crossway's published conditions.

Important constraints to remember:

- API key required
- non-commercial conditions apply
- storage and display limits apply
- attribution is required
- the key must not be shared publicly
- bundling ESV text in the repo is not acceptable

### Product guidance

This is the cleanest licensed translation to support first.

## 2. NIV

### Official path

Biblica's current permissions guidance says NIV app or website use requires written permission, either through:

- an Express License through a ministry partner such as `api.bible` or `platform.youversion.com`, or
- a Standard Publishing License / direct permission request through Biblica

### Important Emmaus-specific implication

Biblica's current Express Licensing path is limited to uses that are:

1. truly non-commercial, and
2. do **not** include any artificial intelligence or machine learning features or functionality

Because Emmaus is an agentic AI study app, we should assume the Express License route may **not** be sufficient for the main Emmaus product.

### Recommended process for NIV

1. Treat NIV as a licensing-first translation, not an implementation-first translation.
2. Contact Biblica through their permissions process.
3. Describe Emmaus clearly as an AI-guided mobile Bible study app.
4. Ask whether NIV can be used in:
   - passage lookup
   - adaptive study sessions
   - mobile delivery
   - limited caching
   - AI-guided workflows
5. Only implement a production NIV provider after written approval or a suitable licensing agreement is in place.

### Product guidance

Do not promise NIV support as a near-term self-serve connection until licensing is clarified.

## 3. NASB

### Official path

The Lockman Foundation publishes permission and quoting guidance for NASB and provides a Permission to Quote Request Form.

The public materials clearly describe quoting permissions and attribution requirements, but they do not present a public self-serve API path comparable to ESV.

### Recommended process for NASB

1. Treat NASB as a permission-first translation.
2. Use the Lockman permission request process.
3. Describe Emmaus as a mobile-first, AI-guided Bible study app.
4. Ask specifically about:
   - app-based display of NASB text
   - passage retrieval in mobile sessions
   - caching limits
   - AI-guided question and reflection workflows
   - attribution requirements inside the app
5. Only implement a dedicated NASB provider after written permission or a clear approved integration path exists.

### Product guidance

NASB is architecturally supportable in Emmaus, but legally and operationally it should be treated like a publisher-approval integration, not like a user-self-serve text source today.

## Recommended Emmaus policy

For now, Emmaus should classify these translations as follows:

### Ready now

- ESV through official API key connection

### Licensing workflow required

- NIV
- NASB

## UX recommendation

The mobile app should let users think in terms of translations, not publishers or provider types.

That means the UI can still offer:

- ESV
- NIV
- NASB

But the setup path beneath each should differ:

- ESV: connect with API key
- NIV: request / connect through approved licensed partner or deployment-level integration only
- NASB: connect only after approved publisher permission or licensed integration is available

## Internal rule for Emmaus development

Before adding any licensed translation provider, confirm all three of these:

1. We know the official rights holder and current terms.
2. We know whether AI-guided use is allowed.
3. We know the exact attribution, caching, and redistribution limits.


## Partner services

Emmaus may eventually support licensed translations through partner Bible platforms such as `API.Bible` or `YouVersion Platform`.

Important principle:

A partner platform can simplify the technical integration, but it does not eliminate translation-level licensing questions.

For Emmaus, partner services are most relevant for:

- NIV
- NASB
- other licensed translations where no clean direct self-serve path exists

### Emmaus policy

- Prefer a direct provider when the official publisher path is clear and supports the Emmaus use case.
- Prefer a partner provider when it meaningfully simplifies multi-translation support and the licensing path is approved for Emmaus's AI-guided behavior.

## MVP recommendation

For MVP, Emmaus should focus on making `ESV` excellent rather than trying to launch multiple licensed translations at once.

That means:

- ESV is the primary licensed translation target
- NIV stays in research and licensing discovery
- NASB stays in research and permission discovery
- partner-provider integrations are a post-MVP or later-phase decision unless licensing clarity improves sooner
