# 07 – Sales & CRM Copilot

## 1. Business Problem & Outcomes

Sales reps spend more time on CRM updates and emails than selling. The Sales Copilot:

  - summarizes calls and updates CRM automatically,
  - drafts personalized outbound emails,
  - flags at-risk deals.

---

## 2. Architecture

### 2.1 Components

  - APIs:
      - `POST /api/v1/sales/call-summary`
      - `POST /api/v1/sales/email-draft`
  - Crew: `SalesCrew`
  - Langflow flows:
      - `sales/call_summary.flow.json`
      - `sales/sales_email.flow.json`
  - MCP virtual server: `sales_toolbox`
  - Tools:
      - `sales.call_summary`
      - `sales.email_generate`
      - `crm.lookup_customer`, `crm.update_opportunity`

---

## 3. Production Setup

### Step 1 – Langflow Flows

  - `call_summary.flow.json`:
      - input: transcript,
      - output: notes, tasks, next steps.
  - `sales_email.flow.json`:
      - input: account info, intent,
      - RAG over case studies & messaging,
      - output: email draft.

### Step 2 – MCP Registration

  - Register call summary and email tools in `sales_toolbox`.
  - Add CRM MCP server for lookup/update operations.

### Step 3 – Config

`config/use_cases/sales.yaml`:

```yaml
id: "sales"
name: "Sales & CRM Copilot"
description: "Call summaries, email drafts, and pipeline insights."
crew: "sales_crew_v1"
langflow_flows:
  call_summary: "sales/call_summary.flow.json"
  email: "sales/sales_email.flow.json"
mcp_virtual_server: "sales_toolbox"
```

Tenant settings:

```yaml
enabled_use_cases:
  - sales
```

## 4. Flow Example – Call Summary

1.  STT engine sends transcript and metadata.
2.  API calls `SalesCrew` with payload.
3.  Crew calls `sales.call_summary` to generate structured summary.
4.  Crew uses `crm.update_opportunity` to write notes and tasks.
5.  Response returned to front-end for rep review.

## 5. Ops Notes

  - Enforce limited CRM operations via tools allow-list.
  - Tune prompts to avoid over-confident summaries.
