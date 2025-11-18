# CrewAI Agents & Crews

We follow a standard pattern for each domain:

- **Intake Agent** – Parse, classify, and normalize user input.
- **RAG Agent** – Retrieve relevant context via MCP or Vector DB.
- **Reasoning Agent** – Use LLM to synthesize a response.
- **Guardrail Agent** – Apply compliance and escalation rules.

Each use case has its own `*Crew` implementation:

- `SupportCrew` – support queries and ticket flows.
- `HRCrew` – HR policy and CV matching.
- `LegalCrew` – contract review and regulatory lookup.

All crews extend `DomainCrew` and should:

1. Keep direct provider usage minimal – always call `llm.gateway.generate`.
2. Use `MCPTool` and `VectorSearchTool` instead of raw HTTP.
3. Return dicts that match the corresponding Pydantic output schema.
