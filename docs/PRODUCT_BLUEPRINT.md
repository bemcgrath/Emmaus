# Emmaus Product Blueprint

## North Star

Emmaus is a personalized Bible study guide.

The app should feel less like a search tool and less like a chatbot, and more like a living study companion that helps the user build a consistent rhythm of reading, reflection, and application.

Its central promise is:

- the guide knows how you study
- the guide helps you stay engaged
- the guide asks questions that deepen insight
- the guide helps turn reflection into action

## Primary User Promise

When a user opens Emmaus, they should feel:

- known: the app remembers their habits, struggles, interests, and recent study history
- guided: the next best study step is suggested, not hidden
- challenged: the app pushes deeper than a summary
- encouraged: progress feels real, visible, and attainable
- grounded: Scripture remains central to the experience

## Core Experience Loop

Each Emmaus session should follow this loop:

1. The guide greets the user with context.
2. The guide proposes a study path based on time, momentum, and recent themes.
3. The user reads the biblical text from their chosen source.
4. The guide asks dynamic questions and adapts based on responses.
5. Optional commentary and cross references are layered in when useful.
6. The guide closes with one action item, prayer prompt, or discussion prompt.
7. The session is logged so the next session becomes smarter.

This loop is the core product engine.

## What The Agent Should Do

The agent is the central orchestrator of the experience. It should not be a single static personality. It should be one guide system with multiple modes, tools, and behaviors.

### Agent responsibilities

The agent should:

- recommend what to study next
- adjust study length based on available time and recent engagement
- generate observation, interpretation, application, and reflection questions
- notice missed sessions and send tailored nudges
- detect patterns such as rushing, shallow answers, or recurring interests
- offer multiple perspectives when useful
- end every session with something concrete to do
- remember what happened in previous sessions so future sessions feel continuous

### Agent modes

Rather than separate products, Emmaus should expose role modes inside one unified guide.

#### Guide mode

Best for:

- introducing a passage
- explaining the structure of the session
- keeping the user moving through the study flow

Behavior:

- calm, pastoral, clear
- suggests the next step
- frames the text and keeps focus on Scripture

#### Peer mode

Best for:

- conversational reflection
- journaling-style dialogue
- processing confusion or emotional reactions

Behavior:

- relational and natural
- asks open questions
- makes the session feel collaborative rather than instructional

#### Challenger mode

Best for:

- deeper reflection
- exposing assumptions
- preventing shallow agreement

Behavior:

- plays devil's advocate carefully
- asks what the user may be avoiding
- surfaces alternative readings or tensions without becoming combative

#### Coach mode

Best for:

- consistency
- habit formation
- follow-through on action items

Behavior:

- tracks streaks and unfinished commitments
- adapts goals when the user is overloaded
- frames progress as a long-term practice rather than a guilt cycle

The system can switch modes explicitly by user choice or implicitly based on the session context.

## Personalization Model

Emmaus should build a living user profile from observed behavior instead of relying only on manual settings.

### Inputs the system should track

- preferred session length
- best study times and days
- completion rate
- passage types the user lingers on most
- question types that produce richer answers
- mood or emotional tone when shared by the user
- action item follow-through
- streak health and return patterns after missed days
- preferred guide mode
- interests such as prayer, theology, leadership, suffering, relationships, wisdom, or gospel themes

### Learning style signals

The system should infer whether the user responds best to:

- short prompts or long prompts
- structured plans or open exploration
- practical application or theological depth
- conversational interaction or guided exercises
- repetition and habit loops or novelty and variety

### Personalization outputs

Based on these signals, Emmaus should adapt:

- study plan length
- tone of the guide
- difficulty of questions
- whether to introduce commentary early or late
- whether to focus on narrative, doctrine, poetry, or thematic studies
- whether to nudge gently or directly
- whether to emphasize reflection, memorization, application, or discussion

## User Interaction Model

Emmaus should support both proactive and reactive interaction.

### Reactive interaction

The user can:

- choose a passage manually
- ask a question about a passage
- request a shorter or deeper session
- switch guide modes
- add notes, prayers, or reflections
- ask for commentary or alternate viewpoints

### Proactive interaction

The guide can:

- suggest a plan when the user opens the app
- remind the user of unfinished action items
- notice a broken streak and propose a low-pressure restart session
- recommend a passage related to recent concerns or themes
- offer a lighter study when the user seems tired or overloaded
- offer a deeper challenge when the user shows strong engagement

### Session entry points

The user should be able to enter Emmaus through several entry points:

- continue where I left off
- I have 10 minutes
- I want to study a topic
- I need encouragement
- I want a deeper challenge
- study with my group
- help me restart after missing a few days

These entry points should shape the first agent response.

## Session Design

Each session should have five stages.

### 1. Orientation

The guide briefly sets the purpose of the session.

Example outcomes:

- continue yesterday's thread
- explore a new passage tied to a theme
- revisit a prior action item

### 2. Reading

The user reads the passage from their selected Bible provider.

The guide can help by:

- choosing a passage length appropriate to the session window
- showing context before and after the passage
- optionally presenting multiple translations if the user has configured them

### 3. Reflection

The guide asks adaptive questions.

Question categories should include:

- observation: what is happening in the text
- interpretation: what it means in context
- connection: how it relates to prior themes or other passages
- reflection: what it surfaces emotionally or spiritually
- application: what should change in response
- discussion: how to bring this into a group conversation

### 4. Expansion

Optional deepening layers can be added:

- commentary notes
- cross references
- alternate viewpoints
- historical background
- word study prompts
- challenge questions from challenger mode

These layers should remain optional so the experience stays focused.

### 5. Response

Every session should end with one concrete takeaway.

Possible outputs:

- an action item for today
- a conversation to have with another person
- a prayer focus
- a memory verse
- a journaling prompt
- a habit commitment for the next session

This is essential. Emmaus should convert reflection into lived practice.

## Dynamic Q&A Strategy

The agent should not wait for the user to ask all the right questions. It should actively propose questions that deepen the study.

### Question engine behavior

The question engine should:

- begin with broad observation questions
- escalate into deeper interpretation when the user is engaged
- pivot to application when the user stays abstract
- ask clarifying questions if the user gives vague answers
- generate related questions when a theme appears repeatedly
- surface tensions, contrasts, or surprises in the text

### Example progression

- What repeats in this passage?
- Why do you think that repetition matters here?
- What assumption would change if you took this verse seriously?
- Where does this challenge your current habits?
- What is one thing you should do differently in the next 24 hours?

## Nudges And Re-engagement

The app should help the user return without feeling manipulative or guilt-driven.

### Nudge types

- momentum nudge: continue a strong streak
- restart nudge: return after a missed window with a smaller session
- theme nudge: suggest a passage connected to a recent concern
- follow-through nudge: remind the user of a prior action item
- encouragement nudge: offer a short guided study when the user reports stress or discouragement

### Nudge personalization

Each nudge should consider:

- preferred time of day
- recent completion behavior
- mood history if available
- whether the user responds better to gentle encouragement or direct challenge
- whether the user is on a streak or in recovery mode

### Anti-burnout rules

The system should:

- reduce intensity after missed sessions
- never shame the user for disengagement
- offer a smaller next step instead of repeating the full prior plan
- cap notification frequency
- allow quiet modes and notification preferences

## Gamification And Community

Gamification should reinforce reflection and consistency, not mere button-tapping.

### Individual progression

Track:

- streaks
- weekly consistency
- completed plans
- action item completion
- topical journeys completed
- reflection depth indicators

### Achievements

Examples:

- seven-day rhythm
- first completed study journey
- five applied action items in a row
- explored all four Gospel accounts on a theme
- comeback badge after restarting following a lapse

### Community features

Potential community loops:

- shared reading challenges
- group study milestones
- prayer or discussion prompts for small groups
- friend accountability check-ins
- optional team streaks
- seasonal challenges such as Advent, Lent, Proverbs month, or Gospel reading plans

### Collaboration vs competition

Emmaus should prefer collaborative motivation over leaderboard obsession.
Competition can exist, but the default emotional posture should be encouragement, shared progress, and accountability.

## Bible Text Consumption Strategy

Emmaus should never hardwire copyrighted Bible text into the core app.

### Text architecture

Use pluggable `BibleTextProvider` adapters.

Provider types:

- local file provider for JSON or similar offline formats
- public-domain bundled sample providers for development and demos
- remote API providers using user-supplied keys
- eventually user-hosted connectors for churches or institutions

### User text setup flow

The user should be able to:

- choose from safe starter options
- connect a Bible API with their own key
- upload or point to a local file
- configure one or more preferred translations
- set a default translation for study

### Text retrieval behavior

The text layer should support:

- passage lookup by reference
- adjacent passage context
- search by keyword or theme metadata if available
- optional multi-translation comparison when the user supplies multiple sources
- caching for passages used in active plans

### Text data boundaries

The app logic should only depend on a normalized passage model.
Providers are responsible for fetching and translating raw source formats into that normalized model.

## Commentary Consumption Strategy

Commentary should be modular, optional, and secondary to the biblical text.

### Commentary architecture

Use pluggable `CommentaryProvider` adapters.

Provider types:

- local commentary files
- public-domain commentary collections
- user-licensed API connectors
- church or group-curated note collections
- personal notes as a commentary layer

### Commentary experience rules

Commentary should:

- never appear before the user has encountered the passage unless explicitly requested
- be clearly labeled by source
- allow multiple viewpoints side by side
- be filterable by tradition, depth, and tone where possible
- remain an optional layer the guide can invite, not force

### Commentary use by the guide

The guide can use commentary to:

- surface helpful context after the user's own observations
- contrast interpretations
- deepen application or theological reflection
- power group study discussions

## Suggested System Architecture

Emmaus should be modeled as one guide system with several internal components.

### Experience orchestrator

Responsible for:

- determining the session type
- choosing the next best action
- coordinating passage, commentary, memory, and Q&A

### Personalization engine

Responsible for:

- user profile updates
- habit detection
- learning style inference
- schedule and nudge timing

### Q&A engine

Responsible for:

- question generation
- follow-up logic
- role-mode behavior
- action item generation

### Content access layer

Responsible for:

- Bible text providers
- commentary providers
- cross-reference providers
- citation and source metadata

### Engagement engine

Responsible for:

- streaks
- reminders
- achievements
- group challenges
- comeback flows

### Memory layer

Responsible for:

- session history
- saved notes
- prior action items
- mood and engagement signals
- preference history

## Proposed API Surface

The current backend scaffold is a good start. Over time, the API should expand toward this model.

### Text and source setup

- `GET /v1/sources/text`
- `POST /v1/sources/text/local`
- `POST /v1/sources/text/api`
- `POST /v1/texts/passage`
- `POST /v1/texts/search`
- `POST /v1/texts/compare`

### Commentary

- `GET /v1/commentary/sources`
- `POST /v1/commentary/lookup`
- `POST /v1/commentary/compare`

### Agent and sessions

- `POST /v1/agent/session/start`
- `POST /v1/agent/session/respond`
- `POST /v1/agent/session/complete`
- `POST /v1/agent/nudges/preview`
- `POST /v1/agent/mode`

### Personalization and memory

- `GET /v1/users/{user_id}/profile`
- `PATCH /v1/users/{user_id}/preferences`
- `GET /v1/study/patterns/{user_id}`
- `POST /v1/study/events`
- `POST /v1/study/action-items`
- `POST /v1/study/mood`

### Engagement

- `GET /v1/engagement/streaks/{user_id}`
- `GET /v1/engagement/challenges`
- `POST /v1/engagement/challenges/{challenge_id}/join`

## MVP Recommendation

To keep the first version focused, MVP should include:

- one-on-one guide sessions
- adaptive study plans based on time and engagement history
- dynamic question generation
- one action item per session
- local and API-based Bible text sources
- placeholder commentary adapters
- streaks and comeback nudges
- basic guide mode and challenger mode

Things to delay until later:

- rich community competition
- deep mood inference from voice or camera
- large social graphs
- complex denominational commentary marketplaces
- advanced multi-agent orchestration visible to the user

## Success Metrics

Emmaus should care less about raw message count and more about meaningful engagement.

Key metrics:

- weekly active studiers
- sessions completed per user per week
- action item completion rate
- streak recovery rate after missed sessions
- average depth of response to reflection prompts
- percent of users who return after the first week
- percent of users who complete a full guided study journey

## Decision Filter

When deciding what to build next, ask:

- Does this strengthen the guide as a personalized companion?
- Does this deepen engagement with Scripture rather than distract from it?
- Does this help the app adapt to the user over time?
- Does this preserve modularity in text, commentary, and AI sources?
- Does this lead to action, not just information?

