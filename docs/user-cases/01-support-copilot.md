# 01 – Customer Support AI Copilot

## 1. Business Problem & Outcomes

Support teams handle large volumes of repetitive tickets across many channels. Knowledge is distributed across FAQs, manuals, and previous tickets. The Support Copilot aims to:

- reduce first-response time and handle time,
- increase first-contact resolution,
- improve answer consistency and quality.

Primary channels: web chat, email, ticketing tools (Zendesk, ServiceNow, custom).

---

## 2. Architecture in the Universal Copilot Platform

### 2.1 Components

- **API route**: `POST /api/v1/support/query`  
- **Schemas**: `SupportQuery`, `SupportReply`
- **Crew**: `SupportCrew` (in `crew/support_crew.py`)
- **Langflow flows**:
  - `support/support_rag.flow.json`
  - `support/support_escalation.flow.json`
- **MCP virtual server**: `support_toolbox` (Context Forge)
- **MCP tools**:
  - `support_rag.query` (Langflow RAG flow)
  - `crm.lookup_customer` (CRM MCP server)
  - `ticket.create` (ticketing MCP server)
- **LLM provider**: resolved per tenant via LLM Gateway (`llm/gateway.py`)

### 2.2 Data & Tools

- KB: FAQs, manuals, troubleshooting, support macros.
- Systems: CRM (customer profile), ticketing system, monitoring/status pages.
- Vector DB: tenant-isolated index `tenant__support__kb`.

---

## 3. Production Setup Checklist

> Prerequisite: platform deployed (backend + Postgres + vector DB + Langflow + Context Forge), and at least one tenant created.

### Step 1 – Configure Langflow Support Flows

1. Open Langflow UI.
2. Import `flows/support/support_rag.flow.json`.
3. Configure:
   - document loaders (KB sources),
   - embedding model (via your preferred provider),
   - vector DB connection (points at `tenant__support__kb`).
4. Export and verify the flow’s ID/slug.
5. Repeat for `support_escalation.flow.json` if you use a separate escalation summarizer.

### Step 2 – Register Langflow as MCP Server

If you use the dedicated Langflow MCP server:

- Deploy `mcp/servers/langflow_tools_server.py` (or use Langflow’s built-in MCP capabilities).
- Ensure tool names:
  - `support_rag.query`
  - `support_escalation.summarize` (if configured)

### Step 3 – Configure Context Forge Virtual Server

In `mcp/config/context-forge-virtual-server.yaml`:

- Under `virtual_servers.support_toolbox`, include:
  - `support_rag.query` from `langflow-tools`
  - `crm.lookup_customer` from `crm` server
  - `ticket.create` from `ticketing` server

Deploy/update Context Forge with this config.

### Step 4 – Configure Use-Case Defaults

In `config/use_cases/support.yaml`:

```yaml
id: "support"
name: "Support Copilot"
description: "AI copilot for customer support interactions and ticket workflows."
crew: "support_crew_v1"
langflow_flows:
  rag: "support/support_rag.flow.json"
  escalation: "support/support_escalation.flow.json"
mcp_virtual_server: "support_toolbox"
```

### Step 5 – Enable for Tenant

In `config/tenants/<tenant>.yaml`:

```yaml
enabled_use_cases:
  - support

llm_policies:
  support:
    provider: "openai"   # or "anthropic" / "watsonx" / "ollama"
    model: "gpt-4.1-mini"
    max_tokens: 2048

tools_allowed:
  support:
    - "support_rag.query"
    - "crm.lookup_customer"
    - "ticket.create"
```

Run migration/seed (or use the admin API) to sync tenant configs into DB.

### Step 6 – Verify API

Ensure backend has reloaded configuration.
Call:

```bash
curl -X POST https://<host>/api/v1/support/query \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: <tenant_id>" \
  -d "{\"message\": \"How do I reset my password?\", \"channel\": \"web\"}"
```

Confirm you receive a `SupportReply` with answer and, ideally, sources.

### Step 7 – Observability & Governance

Confirm `LLMCallLog` entries appear for support calls.
If watsonx.governance is enabled, verify new calls are registered under:

  - Model: external provider / on-prem,
  - Use case: support.

## 4. End-to-End Request Flow

1.  User sends question through UI/Widget (Support Chat Widget).
2.  UI calls `/api/v1/support/query` with `SupportQuery`.
3.  AuthContextMiddleware attaches `tenant_id` and user info.
4.  Route handler:
      - loads tenant config from DB,
      - resolves `SupportCrew` via registry.
5.  SupportCrew:
      - uses `VectorSearchTool` to query `tenant__support__kb`,
      - optionally calls `MCPTool("crm.lookup_customer")`,
      - builds messages and calls `llm.gateway.generate(...)`.
6.  LLM provider (OpenAI/Claude/watsonx/Ollama) returns answer.
7.  SupportCrew constructs `SupportReply` and returns to API.
8.  Logs & metrics stored in DB and, optionally, exported to governance.

## 5. API & Configuration Reference

**Endpoint**

  - `POST /api/v1/support/query`
  - Request: `SupportQuery`
  - Response: `SupportReply`

**Key Config Entries**

  - `config/use_cases/support.yaml` – crew + flows + MCP virtual server.
  - `config/tenants/<tenant>.yaml` – enabled use cases, provider selection, tools allowed.

## 6. Ops & SRE Notes

  - **Scaling**:
      - Backend: horizontally scale pods behind a load balancer.
      - Langflow: scale depending on RAG latency & throughput.
  - **Health Checks**:
      - `/api/v1/health` for FastAPI.
      - Context Forge `/version` endpoint.
  - **Common Issues**:
      - Misconfigured MCP server URLs → tool call failures.
      - Missing embeddings or empty index → poor answers; run ingestion jobs.
  - **Security**:
      - Restrict LLM providers per tenant if data sensitivity is high.
      - Enforce tool allow-list per tenant/use case.
