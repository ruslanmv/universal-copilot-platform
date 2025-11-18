# 05 – Data, BI & Finance Insights Copilot

## 1. Business Problem & Outcomes

Business users need explanations for metrics without waiting for analysts. The Finance Insights Copilot:

  - translates natural language to analytic queries,
  - summarizes results and drivers,
  - links to financial documents for context.

---

## 2. Architecture

### 2.1 Components

  - APIs:
      - `POST /api/v1/finance/query`
  - Crew: `FinanceCrew`
  - Langflow flows:
      - `finance/nl_to_sql.flow.json`
      - `finance/finance_docs_rag.flow.json`
  - MCP virtual server: `finance_toolbox`
  - Tools:
      - `finance.nl_to_sql`
      - `finance_docs_rag.query`
      - data warehouse / analytics engine connector.

---

## 3. Production Setup

### Step 1 – Configure NL→SQL Flow

  - In Langflow:
      - import `nl_to_sql.flow.json`,
      - wire schema metadata (tables, joins) as prompt context,
      - call the data warehouse (Snowflake, BigQuery, etc.) via connectors.

### Step 2 – Configure Finance Docs RAG Flow

  - Import `finance_docs_rag.flow.json`,
  - index:
      - internal reports,
      - board decks,
      - transcripts.

### Step 3 – Expose Tools via MCP

  - `finance.nl_to_sql` mapped to NL→SQL flow.
  - `finance_docs_rag.query` mapped to docs RAG flow.

### Step 4 – Use-Case & Tenant Config

`config/use_cases/finance.yaml`:

```yaml
id: "finance"
name: "Finance Insights Copilot"
description: "Ask questions over data and financial documents."
crew: "finance_crew_v1"
langflow_flows:
  nl_to_sql: "finance/nl_to_sql.flow.json"
  docs_rag: "finance/finance_docs_rag.flow.json"
mcp_virtual_server: "finance_toolbox"
```

Tenant YAML:

```yaml
enabled_use_cases:
  - finance

llm_policies:
  finance:
    provider: "openai"
    model: "gpt-4.1-mini"
    max_tokens: 2048
```

## 4. Flow Example – “Why did EMEA revenue drop in Q3 vs Q2?”

1.  User calls `/api/v1/finance/query`.
2.  `FinanceCrew` calls `finance.nl_to_sql` to generate SQL.
3.  Flow runs query against data warehouse and returns results.
4.  Crew calls `finance_docs_rag.query` to fetch relevant report sections.
5.  LLM Gateway synthesizes narrative + charts + citations.

## 5. Ops Notes

  - Guard against unsafe SQL – enforce schema and allow-list of tables.
  - Ensure governance logging for queries that access sensitive fields.
