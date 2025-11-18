# Governance & IBM watsonx.governance

## Goals

- Track every LLM call for:
  - Cost & usage.
  - Risk classification.
  - Incident analysis.

- Integrate with IBM watsonx.governance as an external model/use-case registry.

## Implementation

1. **LLMCallLog table** records:
   - tenant_id, use_case_id
   - provider/model
   - tokens and latency
   - status and error info

2. **governance logger** module:
   - Hooks into `llm.gateway.generate`.
   - Optionally pushes summaries to watsonx.governance APIs as “external models” and “AI use cases”.

3. **Policies**
   - Enforce which providers and tools can be used per use case.
   - Example: legal and HR flows may be restricted to watsonx.ai or on-prem Ollama models.
