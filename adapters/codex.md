# Codex Adapter

1. Place this repository under `.agent-skills/domain-rules-discovery/` or `skills/domain-rules-discovery/`.
2. Add to the repository instruction file:

```text
For domain discovery tasks, read skills/domain-rules-discovery/SKILL.md and follow it as a mandatory read-only protocol.
```

3. Ask Codex to generate `domain-discovery/` and run:

```bash
python skills/domain-rules-discovery/scripts/validate.py domain-discovery
```
