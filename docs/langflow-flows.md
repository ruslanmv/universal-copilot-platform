# Langflow Flows

Langflow acts as the visual orchestration engine for RAG and document ETL.

## Principles

- Each use case has one or more core flows, stored under `flows/<use_case>/`.
- Flows are versioned as `.flow.json` exports from Langflow UI.
- Flows are imported into a running Langflow via the API (see `scripts/import_flows_to_langflow.py`).

## MCP Integration

Langflow supports MCP as both a server and a client:

- When used as an MCP server, flows are exposed as tools like `support_rag.query`.
- When used as an MCP client, flows can call MCP tools via the **MCP Tools** component.

In our architecture, we typically:

1. Expose Langflow RAG flows as MCP tools.
2. Register them in Context Forge under the `langflow-tools` upstream server.
