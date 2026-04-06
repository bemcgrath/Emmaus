# Translation Provider Strategy

This document defines how Emmaus should think about Bible-text integrations at the architecture level.

## Core decision

Emmaus should support two provider categories:

1. Direct providers
2. Partner providers

The user experience should stay translation-first either way, but the implementation path can differ underneath.

## 1. Direct providers

A direct provider connects Emmaus straight to the publisher or rights holder for a specific translation.

Examples:

- ESV through Crossway

Characteristics:

- translation-specific integration
- publisher-specific API or permission terms
- usually clearer attribution requirements
- often the cleanest path when a good official API already exists

### Emmaus rule

Use a direct provider when:

- the publisher has an official path
- the terms are clear enough for Emmaus's AI-guided use case
- the product benefit is high enough to justify a translation-specific integration

## 2. Partner providers

A partner provider connects Emmaus to a translation-aggregating service rather than directly to one publisher.

Examples:

- API.Bible
- YouVersion Platform

Characteristics:

- one normalized integration can expose many translations
- translation availability still depends on licensing and rights-holder approval
- terms may differ by translation even within the same partner platform
- easier platform architecture, but not automatically easier legal approval

### Emmaus rule

Use a partner provider when:

- we want broader translation coverage through one integration surface
- the partner can legitimately license the translations we want
- the terms allow Emmaus's AI-guided and adaptive study workflows

## MVP decision

For Emmaus MVP, the Bible strategy should be:

- bundled starter Bible for immediate onboarding
- ESV as the primary licensed translation focus
- no production NIV or NASB integration until licensing is clarified
- partner-provider exploration after ESV usability is strong

## Why ESV is the MVP focus

ESV is the best MVP licensed translation because:

- Crossway has a direct official API path
- we already have an ESV connection flow in Emmaus
- it keeps the initial licensing and technical story simpler than NIV or NASB
- it lets us prove the full product loop with a translation many users will actively want

## NIV and NASB posture

For now:

- NIV should be treated as licensing-first, not implementation-first
- NASB should be treated as permission-first, not implementation-first

Emmaus can design for them architecturally now without promising near-term support.

## Architecture guidance

The provider layer should continue to normalize all text sources behind the same app-facing contract.

That means the rest of Emmaus should only care about:

- source identifier
- translation name
- passage text
- attribution / copyright notice
- any user-visible setup state

It should not care whether the source came from:

- a bundled public-domain file
- a direct publisher API
- a partner Bible platform
- a user-uploaded JSON file

## Product guidance

The mobile UI should always ask:

- Which Bible do you want to use?

It should not start by asking:

- Which provider do you want to configure?

Provider complexity belongs underneath the translation choice.

## Near-term build order

1. Make ESV setup and usage feel excellent.
2. Make the bundled starter Bible a smooth fallback.
3. Add stronger source preview and source-state UX.
4. Research partner-provider integrations for NIV and NASB.
5. Add partner-provider support only after licensing terms are confirmed.
