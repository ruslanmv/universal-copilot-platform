# 09 – Legal, Compliance & Risk Copilot

## 1. Business Problem & Outcomes

Legal teams review long contracts and regulations manually. The Legal Copilot:

  - highlights risky clauses,
  - compares contracts to playbooks,
  - links to regulations and policies.

---

## 2. Architecture

### 2.1 Components

  - API:
      - `POST /api/v1/legal/review-contract`
  - Schemas:
      - `ContractReviewRequest`, `ContractReviewResponse`, `ClauseRisk`
  - Crew: `LegalCrew`
  - Langflow flows:
      - `legal/contract_review.flow.json`
      - `legal/regulation_rag.flow.json`
  - MCP virtual server: `legal_toolbox`
  - Tools:
      - `contract_rag.analyse`
      - `regulation_rag.query`
      - `legal_docs.search`

---

## 3. Production Setup

### Step 1 – Clause & Playbook Index

  - `contract_review.flow.json`:
      - split contracts into clauses,
      - compare with standard clause library,
      - annotate deviations.

### Step 2 – Regulation RAG

  - `regulation_rag.flow.json` indexes regulations and guidance.
  - Tools used for cross-reference.

### Step 3 – MCP & Config

  - Register tools, include them in `legal_toolbox`.
  - `config/use_cases/legal.yaml` already defines mapping.

Tenant config:

```yaml
enabled_use_cases:
  - legal

llm_policies:
  legal:
    provider: "ollama"   # or watsonx in strict data environments
    model: "llama3.1-70b"
    max_tokens: 4096
```

## 4. Flow Example – Contract Review

1.  Lawyer uploads contract.
2.  API receives `ContractReviewRequest`.
3.  `LegalCrew`:
      - calls `contract_rag.analyse` to identify key clauses & deviations,
      - calls `regulation_rag.query` for each high-risk clause.
4.  Crew scores risk per clause and suggests changes.
5.  Response returned as `ContractReviewResponse` with overall_risk, clauses, suggestions.

## 5. Ops Notes

  - Prefer on-prem models for legal contents.
  - Ensure logs do not capture full contract text if governance requires redaction.
