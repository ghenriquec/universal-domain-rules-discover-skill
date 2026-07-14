# MCP and Custom Agent Adapter

Expose `SKILL.md`, templates, and schemas as resources. Map abstract operations to available tools:

| Abstract operation | Possible tool |
|---|---|
| Read/search repository | filesystem, git, code search |
| Inspect API | OpenAPI resource, HTTP client |
| Inspect database schema | SQL read-only connection |
| Observe UI | browser automation |
| Run tests | sandboxed shell/CI |
| Write artifacts | filesystem restricted to domain-discovery/ |

The orchestrator must enforce read-only access to product systems.
