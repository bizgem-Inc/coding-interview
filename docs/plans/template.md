# Plan Template

```yaml
---
id: <short-id>
title: <plan title>
status: not_started
owner: <name>
updated_at: YYYY-MM-DD
next_action: <one concrete next action>
file: docs/plans/YYYY-MM-DD_<topic>.md
---
```

## Goal
- <one-sentence goal>

## Scope
- In scope: <items>
- Out of scope: <items>

## Important requirements
- <must-have behavior>

## Transitions
- <transition or N/A>

## Change targets
- <layer and files>

## Tasks
1. <task>
- Deliverables: <deliverables>
- Tests: <tests>

## 要件と自動テストの対応
- <requirement> -> <test>

## Acceptance criteria
- <criterion>

## Notes
- <notes>

## Status update rules
- Use only: `not_started`, `in_progress`, `completed`, `blocked`, `abandoned`.
- When status or next action changes, update `updated_at`.
- Reflect the same status in `docs/plans/index.md`.

## Layer placement checklist

### Domain Layer
- [ ] Entities and NewTypes
- [ ] Domain invariants and pure rules

### Application Layer
- [ ] Repository ports
- [ ] DTOs and Use Cases

### Repositories Layer
- [ ] ORM models and database queries
- [ ] Domain and ORM mapping

### Services Layer
- [ ] HTTP request handling and routes
- [ ] Serializer and outer-to-inner conversion
