# 02 – Enterprise Knowledge Search Copilot

## 1. Business Problem & Outcomes

Employees struggle to find internal policies, design docs, or how-to guides scattered across many content systems. The Knowledge Copilot:

  - provides a single “Ask your company” entry point,
  - respects permissions and document ACLs,
  - returns answers with citations for trust.

---

## 2. Architecture

### 2.1 Components

  - API: `POST /api/v1/knowledge/query`
  - Schemas: `KnowledgeQuery`, `KnowledgeAnswer` (you define these)
  - Crew: `KnowledgeCrew` (`crew/knowledge_crew.py`)
  - Langflow flow: `knowledge/knowledge_rag.flow.json`
  - MCP virtual server: `knowledge_toolbox`
  - Tools:
      - `knowledge_rag.query` (Langflow RAG)
      - `storage.sharepoint.search`
      - `storage.confluence.search`
  - Vector DB indexes:
      - `tenant__knowledge__sharepoint`
      - `tenant__knowledge__confluence`
      - etc.

---

## 3. Production Setup Checklist

### Step 1 – Connect Content Sources in Langflow

1.  Import `knowledge/knowledge_rag.flow.json` in Langflow.
2.  Configure document loaders:
      - SharePoint, Confluence, Google Drive, Git…
3.  Use Langflow’s vector store template to:
      - ingest documents,
      - store embeddings in your vector DB.
4.  Ensure your flow accepts:
      - `query`,
      - `user_id`,
      - `department` or groups, for filtering.

### Step 2 – Expose as MCP Tools

  - Register `knowledge_rag.query` in your Langflow MCP server or Langflow tools server.
  - Optionally, also expose direct search tools:
      - `storage.sharepoint.search`
      - `storage.confluence.search`

### Step 3 – Configure Use Case

`config/use_cases/knowledge.yaml`:

```yaml
id: "knowledge"
name: "Enterprise Knowledge Search"
description: "Ask across all internal docs with access control."
crew: "knowledge_crew_v1"
langflow_flows:
  rag: "knowledge/knowledge_rag.flow.json"
mcp_virtual_server: "knowledge_toolbox"
```

### Step 4 – Enable for Tenant

Update `config/tenants/<tenant>.yaml`:

```yaml
enabled_use_cases:
  - knowledge

llm_policies:
  knowledge:
    provider: "anthropic"
    model: "claude-3.7-sonnet"
    max_tokens: 4096

tools_allowed:
  knowledge:
    - "knowledge_rag.query"
    - "storage.sharepoint.search"
    - "storage.confluence.search"
```

### Step 5 – Test Queries

Sample request:

```bash
curl -X POST https://<host>/api/v1/knowledge/query \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: <tenant_id>" \
  -d "{\"query\": \"What is our EU travel policy?\", \"user_id\": \"u123\"}"
```

Expect: answer text + list of source URLs/IDs.

## 4. Request Flow

1.  User types a question in Knowledge Search widget.
2.  API receives `KnowledgeQuery`, identifies tenant/user.
3.  `KnowledgeCrew`:
      - uses `MCPTool("knowledge_rag.query")`,
      - passes user identity for ACL filtering.
4.  Langflow retrieves allowed documents and drafts an answer.
5.  Crew calls LLM Gateway for final synthesis and redaction.
6.  Answer + citations returned to client.

## 5. Ops Notes

  - Make sure ingestion jobs run regularly to keep indexes fresh.
  - Monitor vector DB usage and index size per tenant.
  - Use tenant-specific indexes for strict isolation.
