# Universal Copilot Platform

<div align="center">

**Enterprise-Grade Multi-Tenant AI Copilot Platform**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-managed-green)](https://github.com/astral-sh/uv)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[Features](#features) •
[Architecture](#architecture) •
[Quick Start](#quick-start) •
[Installation](#installation) •
[Documentation](#documentation) •
[Contributing](#contributing)

</div>

---

## About

The **Universal Copilot Platform** is a production-ready, multi-tenant AI copilot system that enables organizations to deploy and manage 10+ specialized AI use cases from a single codebase. Built on modern AI orchestration frameworks and designed for enterprise scalability, it provides a unified platform for customer support, HR, legal, finance, sales, marketing, and more.

### Key Highlights

- **Multi-Tenant Architecture**: Isolated configurations per tenant with fine-grained access control
- **Provider Agnostic**: Works seamlessly with OpenAI, Anthropic Claude, IBM watsonx.ai, or self-hosted Ollama
- **MCP-First Integration**: Built on Model Context Protocol with IBM mcp-context-forge gateway
- **CrewAI Orchestration**: Sophisticated multi-agent workflows for complex tasks
- **Langflow Integration**: Visual RAG and tool flows for rapid prototyping
- **Production Ready**: Includes monitoring, governance, and enterprise deployment patterns

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🏢 **Multi-Tenancy** | Complete tenant isolation with per-tenant use case configuration |
| 🤖 **Multi-LLM Support** | OpenAI, Anthropic, watsonx.ai, Ollama with unified gateway |
| 🔧 **10+ Use Cases** | Support, HR, Legal, Finance, DevOps, Sales, Marketing, and more |
| 🎯 **MCP Protocol** | Standards-based tool integration via Model Context Protocol |
| 🌊 **Langflow Flows** | 19 pre-built flows for RAG, extraction, and workflow automation |
| 👥 **CrewAI Agents** | Multi-agent orchestration with specialized roles |
| 📊 **Governance & Compliance** | Complete audit logs, token tracking, and usage metrics |
| 🚀 **Cloud Native** | Docker, Kubernetes, OpenShift deployment ready |

### Supported Use Cases

- **Customer Support**: Intelligent ticket routing, knowledge base RAG, escalation management
- **HR & Recruiting**: CV matching, policy Q&A, onboarding automation
- **Legal**: Contract review, clause extraction, regulatory compliance
- **Finance**: NL-to-SQL analytics, document extraction, financial Q&A
- **DevOps/IT**: Code search, documentation RAG, incident management
- **Sales**: Lead qualification, email generation, call summarization
- **Marketing**: Content generation, campaign ideation
- **Healthcare**: Patient history, protocol search, clinical note drafting
- **Knowledge Management**: Enterprise search across all documents
- **Document Processing**: Invoice/claims extraction and classification

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  Multi-tenant routing • Auth • Rate limiting • Health checks │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌─────────────┐
│  LLM Gateway │    │  CrewAI Crews    │    │  MCP Client │
│              │    │                  │    │             │
│ • OpenAI     │    │ • Support Crew   │    │ Context     │
│ • Anthropic  │◄───┤ • HR Crew        │───►│ Forge       │
│ • watsonx.ai │    │ • Legal Crew     │    │             │
│ • Ollama     │    │ • Finance Crew   │    └─────────────┘
└──────────────┘    └──────────────────┘           │
                              │                     │
                    ┌─────────┴─────────┐          │
                    ▼                   ▼          ▼
            ┌──────────────┐    ┌──────────────────────┐
            │   RAG Layer  │    │   MCP Tool Servers   │
            │              │    │                      │
            │ • Vector DB  │    │ • Langflow Flows     │
            │ • Embeddings │    │ • CRM Integration    │
            │ • Chunking   │    │ • HRIS Integration   │
            └──────────────┘    │ • Legal Docs Search  │
                                └──────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Infrastructure & Data Layer                     │
│  PostgreSQL • Qdrant/Milvus • Redis • Langflow • Kubernetes │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Configuration Over Code**: Enable/disable use cases via YAML, not deployments
2. **Gateway Pattern**: Single LLM gateway abstracts provider differences
3. **MCP-First**: All tools exposed via Model Context Protocol for interoperability
4. **Crew-Based**: Each use case is a CrewAI crew + Langflow flows + config
5. **Multi-Tenant Native**: Tenant context flows through every layer

---

## Quick Start

### Prerequisites

- Python 3.11 or 3.12
- Docker & Docker Compose (for local stack)
- `uv` package manager (will be installed automatically)

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/ruslanmv/universal-copilot-platform.git
cd universal-copilot-platform

# 2. Install dependencies
make install

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys (OpenAI, Anthropic, etc.)

# 4. Start the stack
make compose-up

# 5. Run development server
make dev
```

Access the platform:
- **API Documentation**: http://localhost:8000/docs
- **Langflow UI**: http://localhost:7860
- **MCP Context Forge**: http://localhost:4444/admin

---

## Installation

### Using UV (Recommended)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync --all-extras

# Run the application
uv run uvicorn backend.universal_copilot.main:app --reload
```

### Using Make

```bash
# Complete development setup
make setup

# Install dependencies only
make install

# Install with dev tools
make install-dev
```

### Docker

```bash
# Build the image
make docker-build

# Run with docker-compose
make compose-up
```

### Kubernetes

```bash
# Deploy to Kubernetes
make k8s-apply

# Check status
kubectl -n universal-copilot get pods
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Environment
UCP_ENV=dev

# Database
UCP_DATABASE__URL=postgresql+asyncpg://user:pass@localhost:5432/copilot

# Vector Store
UCP_VECTOR_STORE__URL=http://localhost:6333

# Langflow
UCP_LANGFLOW__BASE_URL=http://localhost:7860

# MCP Context Forge
UCP_MCP__CONTEXT_FORGE_URL=http://localhost:4444

# LLM API Keys
UCP_OPENAI_API_KEY=sk-...
UCP_ANTHROPIC_API_KEY=sk-ant-...
UCP_WATSONX_API_KEY=...
UCP_WATSONX_PROJECT_ID=...
```

### Tenant Configuration

Define tenants in `config/tenants/*.yaml`:

```yaml
id: acme-corp
name: Acme Corporation
default_provider: openai
enabled_use_cases:
  - support
  - hr
  - legal

llm_policies:
  support:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
    max_tokens: 4096
  hr:
    provider: openai
    model: gpt-4o
    max_tokens: 2048
```

### Use Case Configuration

Define use cases in `config/use_cases/*.yaml`:

```yaml
id: support
name: Customer Support Copilot
description: Intelligent customer support with RAG and escalation
crew_name: support_crew_v1
flow_ids:
  rag: support/support_rag.flow.json
  escalation: support/support_escalation.flow.json
mcp_virtual_server: support_toolbox
```

---

## Usage

### Python API

```python
from backend.universal_copilot.crew.registry import get_crew
from backend.universal_copilot.schemas.support import SupportQuery

# Get tenant context (from auth middleware in real app)
tenant = {...}

# Get the support crew for this tenant
crew = get_crew("support", tenant)

# Run the crew
query = SupportQuery(
    message="How do I reset my password?",
    channel="web",
)

result = await crew.run_support_flow(query)
print(result.answer)
```

### REST API

```bash
# Query support copilot
curl -X POST http://localhost:8000/api/v1/support/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "How do I reset my password?",
    "channel": "web"
  }'
```

### CLI

```bash
# Run development server
universal-copilot dev

# Run production server
universal-copilot serve --workers 4
```

---

## Development

### Makefile Commands

```bash
make help            # Show all available commands
make install         # Install dependencies
make dev             # Run development server
make test            # Run tests
make test-cov        # Run tests with coverage
make lint            # Run linter
make format          # Format code
make typecheck       # Run type checker
make qa              # Run all quality checks
make ci              # Run full CI pipeline
```

### Code Quality

This project maintains high code quality standards:

- **Linting**: Ruff with comprehensive rule set
- **Formatting**: Ruff formatter (Black-compatible)
- **Type Checking**: MyPy with strict settings
- **Testing**: Pytest with async support
- **Coverage**: Minimum 80% coverage target
- **Pre-commit**: Automated checks before commit

### Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_llm_gateway.py -v

# Run with watch mode
make test-watch
```

---

## Deployment

### Docker Compose (Development/Small Scale)

```bash
# Start the full stack
make compose-up

# View logs
make compose-logs

# Stop the stack
make compose-down
```

### Kubernetes (Production)

```bash
# Deploy to cluster
make k8s-apply

# View logs
make k8s-logs

# Remove deployment
make k8s-destroy
```

### Environment-Specific Configs

- `config/dev.yaml` - Development settings
- `config/prod.yaml` - Production settings with optimizations

---

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Architecture Overview](docs/architecture-overview.md)
- [MCP Architecture](docs/mcp-architecture.md)
- [CrewAI Agents & Crews](docs/crewai-agents-crews.md)
- [Langflow Flows](docs/langflow-flows.md)
- [Governance & Compliance](docs/governance-watsonx.md)
- [Use Case Guides](docs/use-cases/)

---

## Project Structure

```
universal-copilot-platform/
├── backend/
│   └── universal_copilot/
│       ├── main.py              # FastAPI application
│       ├── settings.py          # Configuration management
│       ├── api/                 # REST API routes
│       ├── auth/                # Authentication & multi-tenancy
│       ├── crew/                # CrewAI multi-agent orchestration
│       ├── db/                  # Database models & sessions
│       ├── llm/                 # LLM gateway & providers
│       ├── mcp_host/            # MCP client & server
│       ├── rag/                 # RAG vector search
│       └── schemas/             # Pydantic models
├── config/
│   ├── base.yaml                # Base configuration
│   ├── dev.yaml                 # Development overrides
│   ├── prod.yaml                # Production overrides
│   ├── tenants/                 # Tenant configurations
│   └── use_cases/               # Use case definitions
├── flows/                       # Langflow flow definitions
├── mcp/
│   ├── servers/                 # MCP tool servers
│   └── config/                  # MCP virtual server configs
├── scripts/                     # Utility scripts
├── tests/                       # Test suite
├── infra/
│   ├── k8s/                     # Kubernetes manifests
│   ├── helm/                    # Helm charts
│   └── openshift/               # OpenShift configs
├── docs/                        # Documentation
├── pyproject.toml               # Project metadata & dependencies
├── Makefile                     # Development automation
├── docker-compose.yml           # Local stack orchestration
└── README.md                    # This file
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`make qa`)
5. Run tests (`make test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Add comprehensive docstrings (Google style)
- Include type hints for all functions
- Write tests for new features
- Maintain >80% code coverage

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

```
Copyright 2025 Ruslan Magana

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## Author

**Ruslan Magana**

- Website: [ruslanmv.com](https://ruslanmv.com)
- Email: contact@ruslanmv.com
- GitHub: [@ruslanmv](https://github.com/ruslanmv)

---

## Acknowledgments

Built with these excellent open-source projects:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [CrewAI](https://www.crewai.com/) - Multi-agent orchestration
- [Langflow](https://www.langflow.org/) - Visual AI workflows
- [UV](https://github.com/astral-sh/uv) - Python package manager
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [IBM mcp-context-forge](https://github.com/IBM/mcp-context-forge) - MCP gateway

---

## Support

For support, please:

- Open an issue on [GitHub Issues](https://github.com/ruslanmv/universal-copilot-platform/issues)
- Check the [documentation](docs/)
- Visit [ruslanmv.com](https://ruslanmv.com) for professional services

---

<div align="center">

Made with ❤️ by [Ruslan Magana](https://ruslanmv.com)

**[⬆ Back to Top](#universal-copilot-platform)**

</div>
