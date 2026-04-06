# Emmaus Roadmap

## Purpose

This roadmap turns the Emmaus vision into an implementation sequence.
It is meant to answer one practical question:

What should we build first, what should come next, and what should wait?

The guiding rule is simple:

- build the personalized guide first
- keep the purpose Christ-centered and Scripture-first
- preserve the adaptive cycle of testing, tailoring, and application
- design mobile-first from the beginning
- add engagement loops only when they support real reflection and real-world response

## Current Phase

Emmaus is currently in late `Phase 1` and early `Phase 2`, with a small head start on `Phase 3`.

Current assessment:

- `Phase 1`: substantially complete
- `Phase 2`: actively in progress
- `Phase 3`: lightly started through modular text-source and ESV work

What that means in practice:

- the core personalized guide loop works end to end
- the app already supports mobile-first study, action steps, reminders, and memory continuity
- personalization is real, but still needs more refinement to feel consistently pastoral and nuanced
- content expansion beyond the ESV-first MVP is still intentionally limited
## Phase 0: Foundation

Goal:
Establish the backend and domain boundaries so the rest of the product can evolve cleanly.

Status:
Started and now extended into early Phase 1 work.

Deliverables:

- FastAPI application skeleton
- normalized passage, commentary, user, session, and action-item models
- pluggable Bible text provider interface
- pluggable commentary provider interface
- pluggable LLM provider interface
- initial session lifecycle endpoints
- local sample text source
- project objective, blueprint, and roadmap docs

Exit criteria:

- the app can retrieve a passage from a provider
- the app can run a guided session loop
- the architecture keeps text, commentary, and AI separate

## Phase 1: MVP Personalized Guide

Goal:
Ship the first real Emmaus experience centered on a one-on-one personalized guide that helps users deepen their relationship with Christ through adaptive study.

Why this phase matters:
This is the first version that actually proves the product thesis that the guide is the product and that the adaptive cycle is real.

User experience target:

- a user opens Emmaus on a phone
- the guide suggests a session based on available time and recent history
- the user reads a passage in a mobile-friendly flow
- the guide asks adaptive questions to test understanding and application
- the session ends with one action item, prayer prompt, or reflection
- the system remembers the session and uses it to shape what comes next

Scope:

- user profile basics
- persistent study history
- adaptive session generation
- dynamic Q&A
- action item creation
- streak tracking
- restart nudges
- mobile-first prompt and session design
- ESV-first Bible-source experience for licensed translation support in MVP

Core features:

- persistent storage for users, study events, sessions, and action items
- user preference capture
- session start, respond, and complete endpoints
- time-based session entry points such as `I have 5 minutes` and `I have 10 minutes`
- guide mode
- challenger mode
- one default nudge system
- basic streak engine
- action item logging and completion tracking
- concise prompt formatting intended for mobile UI

Backend work:

- replace in-memory repositories with persistent storage
- add user profile and preferences models
- add session state models
- add action item models
- add basic notification scheduling hooks
- add provider configuration persistence for user text sources

Suggested endpoints:

- `POST /v1/agent/session/start`
- `POST /v1/agent/session/respond`
- `POST /v1/agent/session/complete`
- `GET /v1/users/{user_id}/profile`
- `PATCH /v1/users/{user_id}/preferences`
- `POST /v1/study/action-items`
- `POST /v1/study/action-items/{action_item_id}/complete`
- `GET /v1/engagement/streaks/{user_id}`

Success criteria:

- users can complete a guided session end to end
- the next session reflects the previous one
- every session closes with a concrete next step
- the app supports at least one return loop through streaks or nudges
- the flow feels natural on a smartphone

## Phase 2: Better Personalization

Goal:
Make the guide feel noticeably more tailored to the individual user.

Why this phase matters:
MVP proves the loop. This phase makes the guide feel intelligent, pastoral, and personally relevant rather than generic.

Focus areas:

- habit learning
- learning style adaptation
- schedule-aware nudges
- emotional self-report inputs
- richer question adaptation
- gap detection in understanding and application

Core features:

- preferred session time detection
- preferred session length inference
- learning style signals based on interaction history
- mood check-ins at session start or end
- dynamic difficulty adjustment
- smarter restart flows after missed sessions
- guide tone adaptation
- revisit logic for weak study areas

Backend work:

- add personalization engine service
- add mood event capture
- add nudge decision logic
- add profile summarization for agent prompts
- add session recommendation logic
- add gap scoring for comprehension and application

Success criteria:

- users receive different study plans based on actual behavior
- the guide adjusts to low-energy and high-engagement states
- weak understanding or weak application leads to tailored future study
- nudges become more timely and less generic

## Phase 3: Content Depth

Goal:
Deepen the study experience without losing focus on Scripture or the app's Christ-centered purpose.

Why this phase matters:
Once the guide loop works, Emmaus can become more valuable by layering helpful context and multiple viewpoints.

Focus areas:

- better text consumption
- modular commentary expansion
- optional cross references and alternate views
- stronger study journeys built around repeated weak spots or recurring themes

Core features:

- multi-translation support
- direct-provider support where the official publisher path is strong
- partner-provider support for broader licensed translation coverage after licensing review
- side-by-side passage comparison
- commentary provider selection
- delayed commentary reveal after user reflection
- cross-reference suggestions
- study plans by theme, topic, or book

Success criteria:

- users can study from their preferred text setup
- commentary remains optional and clearly sourced
- the guide can enrich the experience without overshadowing the text

## Phase 4: Engagement And Habit Formation

Goal:
Help users return consistently without making the app feel manipulative, shallow, or guilt-driven.

Why this phase matters:
Emmaus will only be valuable if it becomes part of a person’s ongoing rhythm with Christ in real life.

Focus areas:

- re-engagement loops
- encouragement systems
- action-item follow-through
- comeback experiences
- mobile-friendly habit review and weekly summaries

Core features:

- refined streak system
- comeback badge flows
- weekly study summaries
- unfinished action item reminders
- low-pressure restart sessions
- notification preference controls

Success criteria:

- improved week-two and week-four retention
- meaningful action-item completion rates
- better streak recovery after missed sessions
- users return for spiritual value, not shallow compulsion

## Phase 5: Community And Shared Study

Goal:
Extend Emmaus from personal study into shared rhythms and communal encouragement.

Why this phase matters:
Community can strengthen consistency and application if it supports reflection rather than replacing it.

Focus areas:

- shared plans
- group prompts
- accountability loops
- collaborative challenges

Core features:

- small-group study plans
- shared reading challenges
- team streaks
- group discussion prompts
- friend accountability check-ins
- optional progress sharing

Success criteria:

- users can participate in study with others without losing the personalized guide experience
- community features increase consistency without collapsing into leaderboard-only behavior

## Phase 6: Advanced Guide Intelligence

Goal:
Make the guide more nuanced, more situationally aware, and more helpful over long-term use.

Why this phase matters:
This is where Emmaus starts to feel truly distinct from a basic chat assistant or reading plan app.

Focus areas:

- multi-mode orchestration
- richer memory
- smarter contextual reasoning
- stronger action follow-through

Core features:

- seamless switching between guide, peer, challenger, and coach modes
- theme memory across weeks or months
- deeper action-item follow-up
- contextual recommendations based on recurring struggles or interests
- adaptive long-form study journeys
- better group-aware prompting

Success criteria:

- the guide feels continuous across many sessions
- users experience meaningful variety without losing coherence
- recommendations feel personal rather than scripted

## Phase 7: Optional Stretch Areas

These are valuable, but they should come after the core guide loop is strong.

Potential stretch areas:

- church-specific deployments
- curated public-domain commentary bundles
- advanced analytics dashboards
- audio-first experiences
- voice conversation
- scripture memorization flows
- journaling exports
- sermon or small-group companion modes

## What To Delay On Purpose

These should not be early priorities:

- complex social feeds
- public leaderboards as the main engagement mechanic
- camera-based mood detection
- aggressive notification growth tactics
- heavy marketplace complexity before the core guide is trusted
- multi-agent systems exposed to users before one guide experience is excellent
- desktop-heavy interaction patterns that do not serve the mobile-first experience

## Recommended Build Order

If we want the highest leverage path, build in this sequence:

1. persistent storage and user profiles
2. session lifecycle endpoints
3. action items and completion tracking
4. personalization engine basics
5. gap detection and revisit logic
6. nudges and streaks
7. multi-translation and commentary expansion
8. group challenges and shared study
9. advanced guide modes and long-term memory refinement

## Engineering Milestones

### Milestone 1

Emmaus can run complete personalized study sessions with persistent memory.

### Milestone 2

Emmaus can adapt study rhythm, timing, question depth, and future study choices based on user behavior.

### Milestone 3

Emmaus can support richer content layers through modular text and commentary providers.

### Milestone 4

Emmaus can keep users engaged through healthy nudges, streaks, and action follow-through.

### Milestone 5

Emmaus can support group study and collaborative challenges.

### Milestone 6

Emmaus feels like a long-term personalized guide rather than a sequence of disconnected sessions.

## Product Filter

At every phase, ask:

- does this help users deepen their relationship with Christ through Scripture?
- does this strengthen the adaptive cycle of testing, tailoring, and application?
- does this preserve source modularity?
- does this support a strong mobile-first experience?
- does this encourage real-world response and action?
- does this help the user return for the right reasons?

