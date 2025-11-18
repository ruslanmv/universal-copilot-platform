# 04 – Marketing & Content Studio

## 1. Business Problem & Outcomes

Marketing teams need consistent, on-brand content across many channels and languages. The Marketing & Content Studio:

  - turns campaign briefs into structured content tasks,
  - generates on-brand drafts,
  - learns from performance feedback.

---

## 2. Architecture

### 2.1 Components

  - API: `POST /api/v1/marketing/generate`
  - Crew: `MarketingCrew`
  - Langflow flow: `marketing/marketing_content.flow.json`
  - MCP virtual server: `marketing_toolbox`
  - Tools:
      - `marketing_content.generate`
      - `crm.lookup_customer` (optional for ABM)
      - analytics tools (for performance feedback)

---

## 3. Production Setup

### Step 1 – Configure Langflow Marketing Flow

  - Import `marketing_content.flow.json`.
  - Inputs:
      - campaign brief,
      - target persona,
      - locale & channels.
  - RAG over:
      - product catalog,
      - brand book,
      - previous campaigns.

### Step 2 – Expose as MCP Tool

  - Register as `marketing_content.generate` via Langflow MCP or tools server.
  - Include in `marketing_toolbox` virtual server.

### Step 3 – Use-Case Config

`config/use_cases/marketing.yaml`:

```yaml
id: "marketing"
name: "Marketing & Content Studio"
description: "Campaign planning and content generation."
crew: "marketing_crew_v1"
langflow_flows:
  content: "marketing/marketing_content.flow.json"
mcp_virtual_server: "marketing_toolbox"
```

### Step 4 – Tenant Config

```yaml
enabled_use_cases:
  - marketing

llm_policies:
  marketing:
    provider: "openai"
    model: "gpt-4.1"
    max_tokens: 4096

tools_allowed:
  marketing:
    - "marketing_content.generate"
    - "crm.lookup_customer"
```

### Step 5 – UI Integration

Provide a simple “Campaign Brief” form in admin console or dedicated front-end.
Backend calls `MarketingCrew` which orchestrates planning + content generation.

## 4. Flow Example

1.  Marketer submits a brief for a new product launch.
2.  `MarketingCrew`:
      - normalizes brief,
      - calls `marketing_content.generate` for each asset type.
3.  Langflow flow:
      - fetches product facts & brand guidelines,
      - drafts emails, ads, posts.
4.  Crew runs drafts through “BrandGuard” prompt and returns results for review.

## 5. Ops Notes

  - Brand guidelines evolve – re-ingest docs regularly.
  - Use provider selection to control creativity vs. cost.
