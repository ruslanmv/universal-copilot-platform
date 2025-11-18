# Universal Copilot Platform – Architecture Overview

## High-Level Components

- **Backend API (FastAPI)** – Multi-tenant HTTP API. Routes → crews → LLM gateway → tools.
- **CrewAI Layer** – Domain-specific crews (`support`, `hr`, `legal`, …) orchestrate multi-agent flows.
- **Langflow** – Visual flow engine for RAG, ETL and routing; exposed as MCP tools.
- **LLM Gateway** – Single entrypoint to OpenAI, Anthropic, watsonx.ai and Ollama.
- **MCP & Context Forge** – MCP Gateway that federates MCP servers and REST tools into virtual servers.
- **Vector DB** – Multi-tenant semantic search indexes for RAG.
- **Postgres** – Tenants, configs, logs, governance.

## Request Flow (Support Example)

1. `/api/v1/support/query` receives a `SupportQuery`.
2. Auth middleware injects `tenant_id` into request context.
3. Crew registry resolves `SupportCrew` for that tenant.
4. SupportCrew uses:
   - `VectorSearchTool` (RAG) for tenant’s support KB.
   - `MCPTool("crm.lookup_customer")` via Context Forge if needed.
5. Crew calls `llm.gateway.generate` with provider/model resolved per tenant.
6. Result is normalized as `SupportReply` and returned to caller.
