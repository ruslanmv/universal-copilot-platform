# MCP & Context Forge Architecture

## Model Context Protocol (MCP)

MCP is an open standard that lets AI apps connect to tools, resources and prompts through standardized servers. It defines tools that can be listed and called, with clients discovering capabilities and invoking them securely.

## Context Forge MCP Gateway

Context Forge (mcp-context-forge) is our central MCP gateway and registry:

- Federates multiple MCP servers and REST APIs.
- Exposes a single, secure endpoint to our backend.
- Supports virtual servers like `support_toolbox`, `hr_toolbox`, `legal_toolbox`.

## How We Use It

- **Upstream MCP servers**:
  - `langflow-tools` – RAG flows as tools.
  - `crm-mcp-server`, `hris-mcp-server`, `legal-docs-mcp-server`.
- **Virtual servers**:
  - `support_toolbox` combines RAG, CRM and ticketing tools.
  - `hr_toolbox` combines HR policy RAG and HRIS.
  - `legal_toolbox` combines legal docs search and regulatory RAG.

Our backend uses `MCPClient` to call tools via the gateway, and `mcp_host/server.py` to expose our own crews as tools to external MCP hosts.
