# Agent Instructions

This repository contains a vendor-neutral AI-agent skill.

- `SKILL.md` is the single source of truth.
- Adapters must not redefine or weaken canonical behavior.
- Never modify target application code while executing this skill.
- Write only to `domain-discovery/`.
- Validate JSON outputs before reporting completion.
- Never claim 100% discovery or QA coverage unless the complete real-world rule universe is independently known, which is normally impossible.
