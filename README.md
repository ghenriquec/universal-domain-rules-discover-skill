# Universal Domain Rules Discovery

A vendor-neutral skill for AI agents to discover, extract, compare, validate, and document application-specific domain rules before QA execution.

This repository is designed to work with **any AI agent capable of reading instructions and accessing project artifacts**. It does not depend on a proprietary skill runtime. The canonical behavior lives in `SKILL.md`; platform-specific adapters only explain how to load it.

## Why universal instead of one native format?

There is no single skill format supported by every agent. This repository solves that by separating:

1. **Canonical protocol** — `SKILL.md`
2. **Machine-readable contract** — `manifest.yaml` and JSON Schemas
3. **Platform adapters** — files under `adapters/`
4. **Portable output artifacts** — Markdown and JSON templates
5. **Validation tooling** — `scripts/validate.py`

## Supported usage models

- OpenAI Codex and agent runtimes
- Claude Code
- Cursor
- Gemini CLI
- GitHub Copilot coding agents
- IDE agents
- CI/CD agents
- Autonomous repository agents
- Custom LLM agents
- Any system that accepts a system prompt, repository instruction file, or task policy

## Core promise

The skill guarantees a repeatable **process**, not identical wording. Every compliant agent must:

- trace every rule to evidence;
- separate confirmed rules from hypotheses;
- expose conflicts instead of silently resolving them;
- record gaps and uncertainty;
- generate domain-specific QA scenarios;
- avoid claiming complete coverage without evidence.

## Quick start

### Generic agent

Give the agent this instruction:

```text
Read SKILL.md as a mandatory execution protocol. Analyze the target repository and available product evidence. Produce every required artifact under domain-discovery/. Do not modify application code. Validate JSON outputs against the schemas in schemas/ before finishing.
```

### Repository-level installation

Copy the repository contents into one of these locations:

```text
.agent-skills/domain-rules-discovery/
.ai/skills/domain-rules-discovery/
skills/domain-rules-discovery/
```

Then point the agent to `SKILL.md` from its native instruction mechanism.

## Required output

```text
domain-discovery/
├── domain-overview.md
├── domain-rules.json
├── business-rules-matrix.md
├── state-transition-matrix.md
├── permission-matrix.md
├── calculation-rules.md
├── domain-conflicts.md
├── domain-gaps.md
├── domain-risks.md
├── qa-domain-scenarios.json
├── traceability-matrix.md
└── sources/
    └── source-index.md
```

## Validation

```bash
python scripts/validate.py domain-discovery
```

## Execution modes

- `full`: complete domain discovery
- `incremental`: analyze only changed modules while preserving prior traceability
- `module`: analyze selected modules
- `review`: validate an existing discovery package
- `qa-handoff`: only normalize and export scenarios for a QA skill

## Safety and scope

This skill is read-only by default. It may inspect files, run non-destructive queries, execute tests, and observe application behavior when authorized. It must not modify production data, application code, infrastructure, credentials, or external systems.

## License

MIT
