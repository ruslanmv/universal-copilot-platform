# User Cases – Universal Copilot Platform

This folder documents how to configure and operate each **domain copilot** on the Universal Copilot Platform.

Each copilot is:

- a **CrewAI crew** (multi-agent workflow),
- powered by **Langflow flows** for RAG / data prep,
- connected to enterprise systems via **MCP / Context Forge**,
- using our **LLM Gateway** to route across OpenAI, Claude, watsonx.ai, or Ollama.

## Files

1. `01-support-copilot.md` – Customer Support AI Copilot  
2. `02-knowledge-copilot.md` – Enterprise Knowledge Search  
3. `03-dev-it-copilot.md` – Dev & IT Helpdesk Copilot  
4. `04-marketing-studio.md` – Marketing & Content Studio  
5. `05-finance-insights.md` – Data, BI & Finance Insights Copilot  
6. `06-document-automation.md` – Document Processing & Workflow Automation  
7. `07-sales-copilot.md` – Sales & CRM Copilot  
8. `08-hr-learning-copilot.md` – HR, Recruiting & Learning Copilot  
9. `09-legal-risk-copilot.md` – Legal, Compliance & Risk Copilot  
10. `10-vertical-healthcare-copilot.md` – Vertical Industry Copilot (Healthcare Example)

All use cases share the same **deployment model**:

- You deploy the platform once.
- You enable/disable use cases via **tenant config YAML + admin API** (no new code).
- Each copilot is reachable via a dedicated API route (`/api/v1/<use_case>/...`).

Use this folder as the **runbook** for enabling a new use case for a tenant.
