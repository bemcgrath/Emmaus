# Emmaus Objective

## Purpose

Emmaus exists to guide people into deeper engagement with Scripture through a personalized, adaptive study companion.

The heart of the product is not just Bible reading, note taking, or AI chat.
The heart of the product is an agent that knows the user over time and helps them study with intention, consistency, reflection, and application.

## Core Product Thesis

Emmaus should feel like a wise, trusted study guide that:

- understands the user's habits, schedule, and learning style
- adapts study plans based on prior engagement and momentum
- asks better questions than the user would think to ask alone
- suggests passages, themes, and next steps proactively
- ends each session with a practical action item so reflection leads to lived response

## Product Objective

The objective of Emmaus is to provide an open-source, modular, agentic Bible study app centered on a personalized guide that helps users engage Scripture more deeply through adaptive study plans, dynamic questions, emotional awareness, and actionable next steps, while keeping Bible text and commentary integrations user-controlled and replaceable.

## Principles

Emmaus should always aim to be:

- Scripture-centered: the biblical text remains primary, and the agent serves the text rather than replacing it
- personalized: the guide should adapt to the individual user's habits, pace, questions, and preferred style of learning
- proactive: the agent should not wait passively for commands; it should nudge, suggest, and guide based on context
- reflective: every session should move from reading to understanding to personal response
- modular: text providers, commentary providers, and AI providers must remain decoupled from core application logic
- source-agnostic: the app should work with local files, public-domain texts, or user-supplied APIs
- open-source friendly: the architecture should stay compatible with permissive licensing like MIT
- user-respecting: users should control their sources, workflow, privacy settings, and notification intensity

## What Emmaus Should Do

Emmaus should help users:

- study passages from their chosen Bible source
- receive adaptive plans based on time available, prior engagement, and current momentum
- explore dynamic Q&A that deepens reflection instead of stopping at surface summaries
- engage with the guide in different conversation modes such as mentor, peer, or challenger
- track streaks, milestones, and action-oriented follow-through
- optionally bring in commentary without making commentary the center of the experience
- build a long-term rhythm of Scripture engagement that fits real life

## What Emmaus Should Avoid

Emmaus should avoid becoming:

- a generic AI assistant that only reacts to user prompts
- a closed system tied to a single Bible translation vendor
- an app that bundles copyrighted text without clear rights
- an AI experience detached from the biblical text itself
- a rigid study tool that assumes every user learns the same way
- an architecture where proprietary integrations are mixed into the core domain logic
- a gamified product that rewards activity without spiritual reflection or practical application

## One-Sentence Reference

Emmaus is an open-source, modular, agentic Bible study app centered on a personalized guide that helps people engage Scripture through adaptive plans, meaningful questions, and action-oriented reflection while keeping Bible text and commentary sources user-controlled and replaceable.

## How To Use This Document

When making product, architecture, or feature decisions, use this document to ask:

- Does this strengthen the agent as a personalized guide?
- Does this keep Scripture central?
- Does this preserve modularity between text, commentary, and AI?
- Does this increase user choice, adaptability, and long-term engagement?
- Does this keep the core project clean for open-source distribution?

If a proposed feature conflicts with those goals, it should be redesigned before being added.
