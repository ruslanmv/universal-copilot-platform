# Universal Copilot Platform

Multi-tenant, MCP-first, enterprise-grade copilot platform that runs **all your AI use cases** (support, sales, HR, legal, finance, dev/IT, etc.) on **any LLM provider**:

- OpenAI, Anthropic Claude, IBM watsonx.ai, Ollama (self-hosted)
- CrewAI multi-agent orchestration
- Langflow RAG & tool flows
- IBM **mcp-context-forge** as MCP gateway/registry

The platform is a single app; each “copilot” is just:

> **CrewAI crew + Langflow flow(s) + configuration**

---

## Features

- ✅ **Single codebase**, 10+ enterprise copilots
- ✅ **Multi-tenant**, per-tenant use-case & provider config
- ✅ **Multi-provider LLM gateway** (OpenAI / Claude / watsonx.ai / Ollama)
- ✅ **CrewAI multi-agent orchestration**
- ✅ **Langflow** for visual RAG / tools (via HTTP / MCP)
- ✅ **MCP-first** integration with **IBM mcp-context-forge**
- ✅ **uv-based** Python project (fast, reproducible, modern packaging)
- ✅ **Deployable via Docker, docker-compose, Kubernetes, OpenShift**

---

## Repository Layout (high-level)

```text
.
├── README.md
├── pyproject.toml
├── Makefile
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   └── universal_copilot/
│       ├── main.py
│       ├── settings.py
│       ├── ...
├── config/
│   ├── base.yaml
│   ├── dev.yaml
│   ├── prod.yaml
│   ├── tenants/
│   └── use_cases/
├── infra/
│   ├── k8s/
│   └── openshift/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── docker-build.yml
└── docs/
    └── use-cases/
```

## Quickstart – Local Dev

### Clone the repo

```bash
git clone [https://github.com/your-org/universal-copilot-platform.git](https://github.com/your-org/universal-copilot-platform.git)
cd universal-copilot-platform
```

### Create env file

```bash
cp .env.example .env
# Edit LLM API keys, DB passwords, etc.
```

### Install Python deps with uv

```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
uv sync --locked --all-extras --dev
```

### Run backing services + backend

```bash
# Start Postgres, vector DB, Langflow, MCP Context Forge, etc.
docker compose up -d

# Run API locally with auto-reload
uv run uvicorn backend.universal_copilot.main:app \
  --reload --host 0.0.0.0 --port 8000
```

### Open the API docs

* Backend API: http://localhost:8000/docs
* Langflow UI: http://localhost:7860/
* MCP Gateway (Context Forge): http://localhost:4444/admin

## Production – Docker & docker-compose

```bash
# Build backend image
docker build -f backend/Dockerfile \
  -t ghcr.io/your-org/universal-copilot-backend:latest .

# Run with compose (single box / small env)
docker compose -f docker-compose.yml up -d
```

## Configuration

* Non-secret config in `config/base.yaml`, `config/dev.yaml`, `config/prod.yaml`
* Per-tenant configuration in `config/tenants/*.yaml`
* Secrets (LLM keys, DB creds) via Environment Variables or K8s Secrets.


I’ll walk through **all the files**, but **sorted by importance for development** so a team can actually build this step-by-step and not drown in details.

Think of it as **“what to implement first, second, third…”** and **what goes inside each file**.

---


### 1. `pyproject.toml`  ✅

**Why:** This is the heart of the Python/uv project. Without it, nothing runs.

**Should contain:**

* Project metadata: `name = "universal-copilot-platform"`, version, authors.
* Tooling config for **uv** (dependencies, optional scripts). uv is a fast, all-in-one Python project manager that replaces pip/poetry/pyenv/etc. ([GitHub][1])
* Dependencies:

  * `fastapi`, `uvicorn[standard]` – HTTP API server. ([FastAPI][2])
  * `pydantic` – settings & schemas.
  * `sqlalchemy`, `alembic` – DB + migrations.
  * `httpx` or `aiohttp` – HTTP client (LLM, MCP, Context Forge).
  * `crewai` – multi-agent framework. ([CrewAI Documentation][3])
  * `langflow` client / SDK or generic HTTP client.
  * MCP client library (or generic SSE/WebSocket client) to talk to Context Forge.
  * SDKs: `openai`, Anthropic client, watsonx SDK or generic REST client, etc.
  * `python-dotenv` (optional) for env loading in dev.
* `[project.scripts]` entry:

  * `universal-copilot = "backend.universal_copilot.main:cli"` so devs can run `uvx universal-copilot dev`. ([docs.astral.sh][4])

---

### 2. `backend/universal_copilot/main.py`  ✅

**Why:** FastAPI app entrypoint; everything hangs off this. ([FastAPI][2])

**Should contain:**

* `FastAPI()` app instantiation with metadata (title, version, docs URLs).
* Include routers from `api/router.py`.
* Startup/shutdown events:

  * Initialize DB engine / session maker.
  * Initialize LLM provider registry, quota manager.
  * Initialize MCP host client pointing at Context Forge endpoint.
* Optional CLI using `typer` or `argparse`:

  * `dev` – run uvicorn for local dev.
  * `serve` – production run (delegated to uvicorn/gunicorn in container).

---

### 3. `backend/universal_copilot/settings.py`  ✅

**Why:** Central config; avoids env-variable chaos.

**Should contain:**

* A `Settings` class (Pydantic `BaseSettings`) with fields:

  * `env` (dev/stage/prod), `app_name`, `log_level`.
  * DB URL, vector DB URL, object storage URL.
  * Context Forge MCP endpoint URL.
  * Langflow base URL.
  * API keys / endpoints for OpenAI/Claude/watsonx.ai where appropriate.
* Logic to load:

  * `.env` + `config/base.yaml` + `config/{env}.yaml` + env overrides.
* A singleton getter: `get_settings()`.

---

### 4. `config/base.yaml`, `config/dev.yaml`, `config/prod.yaml`  ✅

**Why:** Non-secret configuration for environments.

**Should contain:**

* Global defaults:

  * HTTP port, log level, feature flags.
  * Default LLM provider/model per use case (can be overridden by tenant).
* `dev.yaml`:

  * Local services endpoints (Local Postgres, local vector DB, local Langflow, local Context Forge).
* `prod.yaml`:

  * External endpoints, timeouts, feature toggles (e.g., disable Swagger).

---

### 5. `backend/universal_copilot/db/session.py`  ✅

**Why:** Single source of truth for DB connection.

**Should contain:**

* `engine = create_engine(settings.DATABASE_URL, ...)`
* `SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)`
* Dependency helpers for FastAPI:

  * `get_db()` that yields a session and handles commit/rollback.

---

### 6. `backend/universal_copilot/db/models.py`  ✅

**Why:** Models for tenants, use cases, providers, logs.

**Should contain (minimum):**

* `Tenant`:

  * `id`, `name`, `default_provider`, `enabled_use_cases`, etc.
* `UseCase`:

  * `id`, `name`, `description`.
* `TenantUseCaseConfig`:

  * `tenant_id`, `use_case_id`, `crew_name`, `flow_ids`, `llm_policy`.
* `ProviderConfig`:

  * mapping tenant → provider → config (no secrets; secrets in env/secret store).
* `LLMCallLog`, `ToolCallLog`:

  * `tenant_id`, `use_case`, `provider`, `model`, `tokens`, `latency`, `status`, etc. (needed for governance & metrics).
* Optional `DocumentSource`, `VectorIndex` for RAG metadata.

---

### 7. `backend/universal_copilot/api/router.py`  ✅

**Why:** Single place to register all routes (modular). ([Medium][5])

**Should contain:**

* `APIRouter()` and `include_router(...)` calls for:

  * `routes_health`, `routes_admin`, `routes_support`, `routes_hr`, etc.
* Versioned path prefix: `/api/v1`.

---

### 8. `backend/universal_copilot/api/routes_health.py`  ✅

**Why:** Health/ready checks for K8s, monitoring.

**Should contain:**

* `GET /health` – returns simple JSON.
* `GET /ready` – checks DB connection and (optionally) Context Forge and Langflow.

---

### 9. `backend/universal_copilot/auth/middleware.py`  ✅

**Why:** Multi-tenant + user context.

**Should contain:**

* FastAPI middleware that:

  * Parses JWT/OIDC token (or API key).
  * Resolves `tenant_id`, `user_id`, roles.
  * Attaches to `request.state` or returns `401/403` if invalid.
* Optional integration with external IdP (Keycloak, Azure AD, etc.).

---

---

## Tier 1 – Domain APIs & Schemas

Once Tier 0 exists, you can serve basic endpoints.

### 10. `backend/universal_copilot/schemas/*.py`  ✅

**Why:** Type-safe IO for each use case (FastAPI + Pydantic). ([realpython.com][6])

**Each file should contain:**

* `support.py`:

  * `SupportQuery(BaseModel)`: `message`, `channel`, optional `metadata`.
  * `SupportReply(BaseModel)`: `answer`, `sources`, `confidence`, `escalation_flag`.
* `hr.py`, `legal.py`, etc.:

  * Request/response models that match the actions of that domain:

    * HR: `HRQuestion`, `CVMatchRequest`, `CVMatchResult`.
    * Legal: `ContractReviewRequest`, `ClauseRisk`, `ContractReviewResponse`.
* Common patterns:

  * Keep them small, strongly typed, with docstrings.

---

### 11. `backend/universal_copilot/api/routes_support.py` (pattern for others)  ✅

**Why:** Entry point for one domain (Support Copilot).

**Should contain:**

* `router = APIRouter(prefix="/support", tags=["support"])`.

* Route like:

  ```python
  @router.post("/query", response_model=SupportReply)
  async def support_query(payload: SupportQuery, deps: = Depends(...)):
      tenant = deps.tenant
      crew = crew_registry.get_crew("support", tenant)
      result = await crew.run_support_flow(payload)
      return result
  ```

* Use dependency injection for:

  * DB session,
  * tenant/auth context,
  * crew registry.

Repeat the same pattern for `routes_hr.py`, `routes_legal.py`, etc. with their own schemas and crew calls.

---

### 12. `config/tenants/*.yaml`  ✅

**Why:** How each tenant “installs” use cases without code changes.

**Each tenant YAML should contain:**

* Basic info: `id`, `name`, `default_provider`.
* `enabled_use_cases`: list like `[support, hr, legal]`.
* `llm_policies`:

  * per use_case: provider + model + max_tokens.
* `tools_allowed`:

  * per use_case: allowed MCP tool names (e.g., `support_rag.query`, `crm.lookup_customer`).

Backend loads these at startup and caches in DB.

---

### 13. `config/use_cases/*.yaml`  ✅

**Why:** Declarative mapping from use-case name to crew and tools.

**Each file should contain:**

* Internal use-case ID and description.
* Default crew name (e.g., `support_crew_v1`).
* Langflow flow IDs (e.g. `support_rag`, `support_escalation`).
* Default MCP virtual server name in Context Forge (e.g. `support_toolbox`).

---

## Tier 2 – AI Core: LLM Gateway, Crews, RAG

These are the “brain” parts.

### 14. `backend/universal_copilot/llm/gateway.py`  ✅✅

**Why:** Single API to all LLM providers + quotas + logging.

**Should contain:**

* `async def generate(tenant_id, use_case, messages, tools=None, **opts)`:

  * Resolve which provider/model to use from tenant + use_case config.
  * Call appropriate provider implementation (`BaseProvider.generate`).
  * Enforce quotas (via `quotas.py`).
  * Log call to `governance/logger.py`.
* Support for:

  * tool calling (if provider supports function/tool schema).
  * streaming (optional).

---

### 15. `backend/universal_copilot/llm/providers/base.py`

**Why:** Abstract interface for providers.

**Should contain:**

* `class BaseProvider(ABC)` with:

  * `name`, `supports_tools`, `supports_streaming`.
  * `async def generate(self, messages, tools=None, **opts)`.

---

### 16. `backend/universal_copilot/llm/providers/openai_provider.py`, `anthropic_provider.py`, `watsonx_provider.py`, `ollama_provider.py`

**Why:** Concrete implementations.

**Each file should contain:**

* Provider-specific config (API base URL, api_key resolution).
* Implementation of `generate(...)` that:

  * Prepares request in provider’s format.
  * Handles errors & retries.
* Example: OpenAI uses Chat Completions; Claude uses Messages; watsonx.ai uses IBM generative endpoints; Ollama calls `POST /api/chat` or `/api/generate` on the local container. ([GitHub][1])

---

### 17. `backend/universal_copilot/crew/base_crew.py`  ✅✅

**Why:** Standard pattern for building a CrewAI crew. ([CrewAI Documentation][7])

**Should contain:**

* Helper for building a `Crew`:

  * Injects:

    * LLM gateway as tool.
    * MCP client tools (so agents can call MCP tools via Context Forge).
    * Shared memory / knowledge configuration.
* Base class for `DomainCrew` with method like `run(payload)` that child crews implement.

---

### 18. `backend/universal_copilot/crew/tools.py`

**Why:** Tools accessible by agents (CrewAI). ([CrewAI Documentation][8])

**Should contain:**

* `MCPTool` wrapper:

  * Knows how to call Context Forge MCP endpoint (via `mcp_host.client`).
  * Accepts a tool name (e.g. `support_rag.query`) and arguments.
* Possibly specialized wrappers:

  * `VectorSearchTool` (calls RAG service).
  * `DBTool` (limited DB queries for analytics, not raw DB).
* Tools should conform to CrewAI tool interface (name, description, args). ([CrewAI Documentation][8])

---

### 19. `backend/universal_copilot/crew/registry.py`

**Why:** Map use-case string → actual crew builder.

**Should contain:**

* `CREW_BUILDERS = {"support": build_support_crew, ...}`
* `def get_crew(use_case: str, tenant: Tenant) -> Crew:` that:

  * Reads `use_cases/*.yaml` and tenant overrides.
  * Instantiates appropriate crew from `*_crew.py`.

---

### 20. `backend/universal_copilot/crew/support_crew.py` (pattern for others)

**Why:** Concrete multi-agent design for Support.

**Should contain:**

* Agent definitions (CrewAI `Agent` objects) with:

  * `SupportIntakeAgent` (classify, parse message).
  * `SupportRAGAgent` (calls MCP tool `support_rag.query`).
  * `SupportAnswerAgent` (LLM reasoning).
  * `GuardrailAgent`.
* Crew definition:

  * `Crew(agents=[...], tasks=[...], process="sequential_or_hierarchical")`.
* A method `async def run_support_flow(payload: SupportQuery) -> SupportReply`.

Replicate similar pattern in `hr_crew.py`, `legal_crew.py`, etc., each with domain-relevant agents. ([CrewAI Documentation][8])

---

### 21. `backend/universal_copilot/rag/vector_client.py`

**Why:** RAG vector DB abstraction.

**Should contain:**

* Client wrapper for chosen vector DB (Milvus, pgvector, etc.), tuned for multi-tenancy. ([FastAPI][2])
* Methods:

  * `create_index(tenant_id, use_case, name)`.
  * `upsert(tenant_id, use_case, docs: list)`.
  * `query(tenant_id, use_case, query_text, top_k)`.

---

### 22. `backend/universal_copilot/rag/indexes.py`

**Why:** Consistent naming & partitioning.

**Should contain:**

* Functions to build index names:

  * `def index_name(tenant_id, use_case, source):`
  * e.g. `tenantA__support__kb`.
* Optional helper to map to vector partitions/collections.

---

### 23. `backend/universal_copilot/rag/ingestion.py`

**Why:** Document ingestion pipeline.

**Should contain:**

* Functions like:

  * `ingest_from_sharepoint(tenant, use_case, site_url, ...)`
  * `ingest_from_confluence(...)`
* Pipeline steps:

  * load → clean → chunk → embed → store via `vector_client`.

---

## Tier 3 – MCP & Context Forge Integration

These make the app **standards-aligned** and “plug-and-play” with the MCP ecosystem.

### 24. `backend/universal_copilot/mcp_host/client.py`  ✅✅

**Why:** Our platform as MCP host, calling tools via Context Forge.

**Should contain:**

* A client that:

  * Maintains connection to Context Forge’s MCP endpoint (supports SSE/HTTP/WebSocket). ([GitHub][9])
  * Exposes `async def call_tool(tool_name, args, tenant_context)`:

    * add tenant context in metadata.
    * invoke MCP tool via Context Forge (which routes to correct server or REST).
* Optional caching of tool schema descriptions.

---

### 25. `backend/universal_copilot/mcp_host/server.py` (optional but powerful)

**Why:** Let *other* MCP hosts (Claude desktop, ChatGPT, IDEs) use your platform as a tool server. ([CrewAI Documentation][3])

**Should contain:**

* Implementation of MCP server protocol:

  * Tool definitions like `support.answer_ticket`, `legal.review_contract`.
  * When invoked, those tools call the corresponding crews inside your backend.
* Runs as part of the same container or as a small sidecar.

---

### 26. `mcp/servers/langflow_tools_server.py`

**Why:** MCP server that exposes Langflow flows as tools. ([Langflow Documentation][10])

**Should contain:**

* MCP server implementation with tools:

  * `support_rag.query(inputs)`: calls Langflow HTTP API for the `support_rag` flow and returns response.
  * `hr_policy_rag.query`, etc.
* Uses `flows/*.flow.json` ids to know which flow to call.

(You may alternatively let Langflow be an MCP server itself and just register it in Context Forge. Docs show Langflow can be MCP server & client. ([Langflow Documentation][10]))

---

### 27. `mcp/servers/*.py` (CRM, HRIS, Legal docs, etc.)

**Why:** Wrap legacy REST APIs into MCP tools, if you don’t want to define them only in Context Forge.

**Each file should contain:**

* Tools that call a specific system:

  * `crm.lookup_customer` → REST call to CRM.
  * `hr.get_employee_benefits` → HRIS call.
  * `legal_docs.search` → internal legal doc search.

---

### 28. `mcp/config/context-forge-virtual-server.yaml`  ✅

**Why:** Define tool sets (virtual servers) in Context Forge. ([GitHub][9])

**Should contain:**

* Config describing:

  * Upstream MCP servers (Langflow server, CRM server, HR server, etc.).
  * Virtual servers for:

    * `support_toolbox` – includes `support_rag.query`, `crm.lookup_customer`, `ticket.create`.
    * `hr_toolbox` – HR-related tools.
    * `legal_toolbox` – legal tools.
* Auth & rate limit policies per virtual server.

---

### 29. `infra/k8s/mcp-context-forge-deployment.yaml` & `mcp-context-forge-service.yaml`

**Why:** Actually run Context Forge in your cluster. ([GitHub][9])

**Should contain:**

* Deployment with:

  * Container image `ghcr.io/ibm/mcp-context-forge:tag` (or similar).
  * Env vars for Redis (if used), config mount for MCP server registry.
* Service exposing MCP endpoint inside cluster.

---

## Tier 4 – Infra, Dev UX, Frontend, Docs

These make the platform usable and deployable.

### 30. `docker-compose.yml`

**Why:** Easiest way for devs to run everything locally.

**Should contain:**

* Services:

  * `backend` – FastAPI + CrewAI.
  * `langflow` – Langflow server (MCP-enabled). ([Langflow Documentation][10])
  * `mcp-context-forge`.
  * `postgres`.
  * `vector-db` (Milvus/Weaviate/pgvector).
  * `ollama` (optional for local models). ([GitHub][1])

---

### 31. `infra/helm/*` & `infra/k8s/*`

**Why:** Production-ready deployment (Kubernetes).

**Should contain:**

* `values.yaml` – toggles for each service, resource limits.
* Templates:

  * backend Deployment + Service.
  * Langflow Deployment + Service.
  * Context Forge Deployment + Service.
  * Postgres & vector DB statefulsets.
  * Ingress routing to backend + Langflow UIs.

---

### 32. `frontend/admin-console/*`

**Why:** Admin UI to manage tenants, providers, use cases.

**Important contents:**

* `pages/TenantsPage.tsx`:

  * CRUD for tenant configs (id, enabled use cases, provider prefs).
* `pages/UseCasesPage.tsx`:

  * Toggle which use cases are active for each tenant.
* `pages/ProvidersPage.tsx`:

  * Manage provider configs per tenant.
* Components to:

  * Show LLM usage metrics.
  * Show errors/logs per tenant/use case.

---

### 33. `frontend/widgets/*`

**Why:** Drop-in client widgets:

* `support-chat-widget`:

  * `SupportChat.tsx` → front-end chat UI, calling `/api/support/query`.
  * `embed.js` → snippet to add `<script src=...>`, auto-mount widget on customer site.
* `knowledge-search-widget`:

  * Minimal search bar + results panel.

---

### 34. `docs/*`

**Why:** Reference for new devs and ops.

* `architecture-overview.md`:

  * Explain layers (MCP host, Context Forge, CrewAI, Langflow, LLM gateway).
* `crewai-agents-crews.md`:

  * Patterns for designing agents & crews. ([CrewAI Documentation][8])
* `langflow-flows.md`:

  * How to design flows and expose them as MCP tools in Langflow. ([Langflow Documentation][10])
* `mcp-architecture.md`:

  * How Context Forge sits between MCP servers & our backend, plus examples of virtual server config. ([GitHub][9])
* `governance-watsonx.md`:

  * How model calls are logged and exported to watsonx.governance as external models/use cases. ([GitHub][1])

---

### 35. `scripts/install.sh`

**Why:** One-command dev setup using uv.

**Should contain:**

* Shell script that:

  * Installs uv if missing (using official installer). ([docs.astral.sh][11])
  * Runs `uv sync`.
  * Runs `docker-compose up -d` for infra.
  * Runs `uvx universal-copilot dev`.

---

### 36. `scripts/init_dev_data.py`, `scripts/load_demo_documents.py`, `scripts/import_flows_to_langflow.py`

**Why:** Developer convenience.

* `init_dev_data.py`:

  * Creates example tenants and use-case configs in DB.
* `load_demo_documents.py`:

  * Loads sample docs for each use case into vector DB.
* `import_flows_to_langflow.py`:

  * Reads `flows/*.flow.json` and uses Langflow API to import them. ([Langflow Documentation][10])

---
