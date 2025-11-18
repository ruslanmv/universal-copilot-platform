# 03 – Dev & IT Helpdesk Copilot

## 1. Business Problem & Outcomes

Developers and IT staff spend time reading legacy code and answering repeated IT questions. The Dev & IT Copilot:

  - explains code and architecture on demand,
  - accelerates IT helpdesk with self-service,
  - reduces time to resolve tickets.

---

## 2. Architecture

### 2.1 Components

  - APIs:
      - `POST /api/v1/dev/query` (code questions)
      - `POST /api/v1/it/query` (IT tickets)
  - Crews:
      - `DevCrew` (code RAG & explanation)
      - `ITHelpdeskCrew` (IT KB & workflows)
  - Langflow flows:
      - `dev_it/code_rag.flow.json`
      - `dev_it/it_kb_rag.flow.json`
  - MCP virtual servers:
      - `dev_toolbox`, `it_toolbox`
  - Tools:
      - `code_rag.query` (codebase RAG)
      - `it_kb_rag.query`
      - `ticket.servicenow.*` or `ticket.jira.*`

---

## 3. Production Setup

### Step 1 – Index Code & IT KB via Langflow

  - For `code_rag.flow.json`:
      - connect to Git, monorepos, docs,
      - chunk and embed functions/files.
  - For `it_kb_rag.flow.json`:
      - include runbooks, IT policies, known issues.

### Step 2 – MCP Registration

  - Export flows as tools:
      - `code_rag.query`
      - `it_kb_rag.query`
  - Configure Context Forge:
      - `dev_toolbox` includes code RAG + maybe CI/CD tools.
      - `it_toolbox` includes IT KB + ticketing tools.

### Step 3 – Use Case Config Files

`config/use_cases/dev_it.yaml`:

```yaml
id: "dev_it"
name: "Dev & IT Copilot"
description: "Code understanding and IT helpdesk assistance."
crew: "dev_it_crew_v1"
langflow_flows:
  code_rag: "dev_it/code_rag.flow.json"
  it_kb_rag: "dev_it/it_kb_rag.flow.json"
mcp_virtual_server: "dev_toolbox"
```

(You can split dev vs IT into separate use cases if needed.)

### Step 4 – Tenant Enablement

Add to tenant config:

```yaml
enabled_use_cases:
  - dev_it

llm_policies:
  dev_it:
    provider: "openai"
    model: "gpt-4.1"
    max_tokens: 4096
```

### Step 5 – IDE / Chat Integration

  - For devs: expose `/api/v1/dev/query` in IDE extensions (VS Code, JetBrains).
  - For IT: embed a chat widget connected to `/api/v1/it/query`.

## 4. Flow Example (Dev Question)

1.  Developer selects code snippet → “Explain”.
2.  IDE plugin calls `/api/v1/dev/query`.
3.  `DevCrew` calls `code_rag.query` for related code & docs.
4.  Crew uses LLM Gateway to generate explanation and optional refactor suggestion.
5.  Response returned to IDE.

## 5. Ops Notes

  - Code indexes can be large → ensure vector DB cluster can handle load.
  - For sensitive code, enforce on-prem providers (Ollama, watsonx).
