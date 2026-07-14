# OpenAI Agents SDK Adapter

Load the content of `SKILL.md` into the agent's instructions or retrieve it as a repository knowledge file. Provide filesystem/search tools as available. Restrict write access to `domain-discovery/`.

Recommended guardrail:

```text
Reject writes outside domain-discovery/ and reject destructive shell/database commands.
```
