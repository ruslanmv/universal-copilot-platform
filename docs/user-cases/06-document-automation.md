# 06 – Document Processing & Workflow Automation

## 1. Business Problem & Outcomes

Organizations process invoices, claims, and forms manually. The Document Automation Copilot:

  - extracts structured data from documents,
  - validates against business rules,
  - triggers workflows and drafts responses.

---

## 2. Architecture

### 2.1 Components

  - APIs:
      - `POST /api/v1/documents/process`
  - Crew: `DocumentAutomationCrew`
  - Langflow flows:
      - `documents/invoice_extraction.flow.json`
      - `documents/claims_extraction.flow.json`
  - MCP virtual server: `documents_toolbox`
  - Tools:
      - `invoice_extraction.run`
      - `claims_extraction.run`
      - ERP / claims system MCP tools.

---

## 3. Production Setup

### Step 1 – Document Extraction Flows

  - In Langflow, build flows that:
      - run OCR / parsing,
      - use layout-aware components if needed,
      - prompt an LLM to output JSON.

### Step 2 – MCP Registration

  - Map flows to tools:
      - `invoice_extraction.run`
      - `claims_extraction.run`

### Step 3 – Use-Case Config

`config/use_cases/documents.yaml`:

```yaml
id: "documents"
name: "Document Automation Copilot"
description: "Invoices, claims and form processing."
crew: "documents_crew_v1"
langflow_flows:
  invoice: "documents/invoice_extraction.flow.json"
  claims: "documents/claims_extraction.flow.json"
mcp_virtual_server: "documents_toolbox"
```

### Step 4 – Tenant Setup

  - Enable `documents` use case.
  - Provide ERP connection parameters via secrets/config.

## 4. Flow Example – Invoice

1.  Invoice PDF arrives → ingestion pipeline stores and triggers API.
2.  `DocumentAutomationCrew` calls `invoice_extraction.run`.
3.  Flow returns JSON fields (vendor, amount, dates, line items).
4.  Crew validates against ERP (vendor registry, purchase orders).
5.  If valid, creates invoice record and drafts email to supplier.

## 5. Ops Notes

  - Keep training examples and extraction prompts under version control.
  - Monitor extraction quality metrics (field accuracy, exception rate).
