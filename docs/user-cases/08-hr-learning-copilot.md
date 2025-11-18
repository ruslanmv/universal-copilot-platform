# 08 – HR, Recruiting & Learning Copilot

## 1. Business Problem & Outcomes

HR teams handle repetitive Q&A, manual CV screening, and generic learning plans. The HR Copilot:

  - answers HR questions with policy-aware RAG,
  - scores CVs against job descriptions,
  - proposes learning paths.

---

## 2. Architecture

### 2.1 Components

  - APIs:
      - `POST /api/v1/hr/question`
      - `POST /api/v1/hr/cv-match`
  - Schemas:
      - `HRQuestion`, `HRAnswer`
      - `CVMatchRequest`, `CVMatchResult`
  - Crew: `HRCrew`
  - Langflow flows:
      - `hr/hr_policy_rag.flow.json`
      - `hr/cv_matching.flow.json`
  - MCP virtual server: `hr_toolbox`
  - Tools:
      - `hr_policy_rag.query`
      - `cv_matching.run`
      - `hr.get_employee_benefits` (HRIS MCP server)

---

## 3. Production Setup

### Step 1 – Policy RAG Flow

  - Ingest HR policies and procedures (per region).
  - Flow takes `question + employee metadata` and returns answer + references.

### Step 2 – CV Matching Flow

  - Input: CV text + JD text.
  - Output: match score, key skills, gaps.

### Step 3 – MCP Registration & Config

  - Map flows to `hr_policy_rag.query` and `cv_matching.run`.
  - Include them in `hr_toolbox`.
  - `config/use_cases/hr.yaml`:

```yaml
id: "hr"
name: "HR & Learning Copilot"
description: "HR Q&A, CV matching and learning recommendations."
crew: "hr_crew_v1"
langflow_flows:
  policy_rag: "hr/hr_policy_rag.flow.json"
  cv_matching: "hr/cv_matching.flow.json"
mcp_virtual_server: "hr_toolbox"
```

## 4. Flow Example – CV Match

1.  Recruiter uploads CV and selects JD.
2.  API receives `CVMatchRequest`.
3.  `HRCrew` calls `cv_matching.run`.
4.  Flow returns match score and explanation.
5.  Crew optionally calls HRIS to enrich with internal data (internal candidate).

## 5. Ops Notes

  - Carefully design prompts to avoid biased wording in explanations.
  - Use governance to audit model behavior on HR use cases.
