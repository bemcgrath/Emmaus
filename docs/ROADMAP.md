# Emmaus Roadmap

## Purpose

This roadmap turns the Emmaus vision into an implementation sequence.
It is meant to answer one practical question:

What should we build first, what should come next, and what should wait?

The guiding rule is simple:

- build the personalized guide first
- keep Scripture central
- preserve modularity in text, commentary, and AI
- add engagement loops only when they support real reflection and action

## Phase 0: Foundation

Goal:
Establish the backend and domain boundaries so the rest of the product can evolve cleanly.

Status:
Mostly started through the current scaffold.

Deliverables:

- FastAPI application skeleton
- normalized passage, commentary, and study models
- pluggable Bible text provider interface
- pluggable commentary provider interface
- pluggable LLM provider interface
- basic agent session endpoint
- local sample text source
- project objective and product blueprint docs

Exit criteria:

- the app can retrieve a passage from a provider
- the app can generate a simple guided study response
- the architecture keeps text, commentary, and AI separate

## Phase 1: MVP Personalized Guide

Goal:
Ship the first real Emmaus experience centered on a one-on-one personalized guide.

Why this phase matters:
This is the first version that actually proves the product thesis that the guide is the product.

User experience target:

- a user opens Emmaus
- the guide suggests a session based on available time and recent history
- the user reads a passage
- the guide asks adaptive questions
- the session ends with one action item
- the system remembers the session for next time

Scope:

- user profile basics
- persistent study history
- adaptive session generation
- dynamic Q&A
- action item creation
- streak tracking
- restart nudges

Core features:

- persistent storage for users, study events, and action items
- user preference capture
- session start, respond, and complete endpoints
- time-based session entry points such as `I have 10 minutes`
- guide mode
- challenger mode
- one default nudge system
- basic streak engine
- action item logging and completion tracking

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

## Phase 2: Better Personalization

Goal:
Make the guide feel noticeably more tailored to the individual user.

Why this phase matters:
MVP proves the loop; this phase makes the guide feel intelligent and relational rather than generic.

Focus areas:

- habit learning
- learning style adaptation
- schedule-aware nudges
- emotional self-report inputs
- richer question adaptation

Core features:

- preferred session time detection
- preferred session length inference
- learning style signals based on interaction history
- mood check-ins at session start or end
- dynamic difficulty adjustment
- smarter restart flows after missed sessions
- guide tone adaptation

Backend work:

- add personalization engine service
- add mood event capture
- add nudge decision logic
- add profile summarization for agent prompts
- add session recommendation logic

Suggested endpoints:

- `POST /v1/study/mood`
- `GET /v1/agent/recommendations/{user_id}`
- `POST /v1/agent/nudges/preview`
- `POST /v1/agent/mode`

Success criteria:

- users receive different study plans based on actual behavior
- the guide adjusts to low-energy and high-engagement states
- nudges become more timely and less generic

## Phase 3: Content Depth

Goal:
Deepen the study experience without losing focus on the biblical text.

Why this phase matters:
Once the guide loop works, Emmaus can become more valuable by layering helpful context and multiple viewpoints.

Focus areas:

- better text consumption
- modular commentary expansion
- optional cross references and alternate views

Core features:

- multi-translation support
- side-by-side passage comparison
- commentary provider selection
- delayed commentary reveal after user reflection
- cross-reference suggestions
- study plans by theme, topic, or book

Backend work:

- add text comparison endpoint
- add search endpoint if metadata allows
- add commentary comparison support
- add source ranking and defaults per user
- add content caching for active plans

Suggested endpoints:

- `POST /v1/texts/search`
- `POST /v1/texts/compare`
- `POST /v1/commentary/compare`

Success criteria:

- users can study from their preferred text setup
- commentary remains optional and clearly sourced
- the guide can enrich the experience without overshadowing the text

## Phase 4: Engagement And Habit Formation

Goal:
Help users return consistently without making the app feel manipulative or shallow.

Why this phase matters:
Emmaus will only be valuable if it becomes part of a person’s ongoing rhythm.

Focus areas:

- re-engagement loops
- encouragement systems
- action-item follow-through
- comeback experiences

Core features:

- refined streak system
- comeback badge flows
- weekly study summaries
- unfinished action item reminders
- low-pressure restart sessions
- notification preference controls

Backend work:

- engagement engine service
- achievement rules
- weekly summary generation
- notification queue integration

Suggested endpoints:

- `GET /v1/engagement/summary/{user_id}`
- `GET /v1/engagement/achievements/{user_id}`
- `POST /v1/engagement/notifications/preferences`

Success criteria:

- improved week-two and week-four retention
- meaningful action-item completion rates
- better streak recovery after missed sessions

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

Backend work:

- group models and permissions
- challenge models
- group session prompts
- shared milestone tracking

Suggested endpoints:

- `GET /v1/engagement/challenges`
- `POST /v1/engagement/challenges/{challenge_id}/join`
- `POST /v1/groups`
- `POST /v1/groups/{group_id}/plans`

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

Backend work:

- stronger memory summarization
- session-to-session thematic linking
- richer personalization prompt assembly
- advanced guide policy layer

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

## Recommended Build Order

If we want the highest leverage path, build in this sequence:

1. persistent storage and user profiles
2. session lifecycle endpoints
3. action items and completion tracking
4. personalization engine basics
5. nudges and streaks
6. multi-translation and commentary expansion
7. group challenges and shared study
8. advanced guide modes and long-term memory refinement

## Engineering Milestones

### Milestone 1

Emmaus can run complete personalized study sessions with persistent memory.

### Milestone 2

Emmaus can adapt study rhythm, timing, and question depth based on user behavior.

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

- does this strengthen the guide as the central experience?
- does this deepen scripture engagement?
- does this preserve source modularity?
- does this encourage real-world response and action?
- does this help the user return for the right reasons?
