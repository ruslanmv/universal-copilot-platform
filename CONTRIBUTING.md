# Contributing to Universal Copilot Platform

Thank you for your interest in contributing to the Universal Copilot Platform! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and constructive in all interactions
- Focus on what is best for the community
- Show empathy towards other community members
- Accept constructive criticism gracefully

## Getting Started

### Prerequisites

- Python 3.11 or 3.12
- [UV](https://github.com/astral-sh/uv) package manager
- Git
- Docker and Docker Compose (for testing full stack)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/universal-copilot-platform.git
   cd universal-copilot-platform
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ruslanmv/universal-copilot-platform.git
   ```

4. **Install dependencies**:
   ```bash
   make install
   # or
   make setup  # includes pre-commit hooks
   ```

5. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests
- `chore/` - Maintenance tasks

Examples:
- `feature/support-crew-memory`
- `fix/llm-gateway-timeout`
- `docs/update-deployment-guide`

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```
feat(llm): add support for Gemini provider

Implemented Gemini provider with proper error handling
and streaming support.

Closes #123
```

```
fix(crew): resolve memory leak in support crew

Fixed issue where conversation history was not being
properly cleaned up after each run.

Fixes #456
```

### Running Quality Checks

Before committing, ensure all quality checks pass:

```bash
# Run all quality checks
make qa

# Individual checks
make lint          # Linting
make format-check  # Format checking
make typecheck     # Type checking
make test          # Tests
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks before each commit:

```bash
make pre-commit-install
```

The hooks will automatically:
- Format code with Ruff
- Run linters
- Check for common issues
- Validate commit messages

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications enforced by Ruff:

- **Line length**: 100 characters
- **Quotes**: Double quotes for strings
- **Indentation**: 4 spaces (no tabs)
- **Import order**: stdlib, third-party, local (enforced by isort)

### Type Hints

All functions must include type hints:

```python
from typing import Optional

def process_query(
    query: str,
    tenant_id: str,
    max_tokens: Optional[int] = None,
) -> dict[str, Any]:
    """Process a query for a specific tenant.

    Args:
        query: The user's query string.
        tenant_id: Unique identifier for the tenant.
        max_tokens: Maximum tokens for the response. Defaults to None.

    Returns:
        Dictionary containing the response and metadata.

    Raises:
        ValueError: If query is empty.
        TenantNotFoundError: If tenant doesn't exist.
    """
    ...
```

### Docstrings

Use Google-style docstrings for all modules, classes, and functions:

```python
"""Module for LLM provider implementations.

This module contains abstract base classes and concrete implementations
for various LLM providers including OpenAI, Anthropic, and watsonx.ai.
"""

class OpenAIProvider(BaseProvider):
    """OpenAI LLM provider implementation.

    Provides integration with OpenAI's Chat Completions API with support
    for tool calling, streaming, and error handling.

    Attributes:
        api_key: OpenAI API key from environment.
        base_url: Optional custom API base URL.

    Example:
        >>> provider = OpenAIProvider()
        >>> response = await provider.generate(
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     model="gpt-4o"
        ... )
    """
    ...
```

### Error Handling

- Use specific exception types
- Provide descriptive error messages
- Log errors appropriately
- Use try-except blocks judiciously

```python
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

class ProviderError(Exception):
    """Base exception for provider errors."""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
async def call_llm_api(self, payload: dict) -> dict:
    """Call LLM API with retry logic."""
    try:
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API error: {e.response.status_code}")
        raise ProviderError(f"API request failed: {e}") from e
    except httpx.TimeoutException as e:
        logger.error("LLM API timeout")
        raise ProviderError("API request timed out") from e
```

### Logging

Use `loguru` for logging with appropriate levels:

```python
from loguru import logger

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning about potential issues")
logger.error("Error that needs attention")
logger.critical("Critical error requiring immediate attention")
```

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory mirroring the source structure
- Name test files as `test_*.py`
- Use descriptive test names that explain what is being tested
- Follow AAA pattern: Arrange, Act, Assert

```python
import pytest
from backend.universal_copilot.llm.gateway import LLMGateway

@pytest.mark.asyncio
async def test_llm_gateway_routes_to_correct_provider():
    """Test that LLM gateway correctly routes requests based on tenant config."""
    # Arrange
    gateway = LLMGateway()
    tenant_id = "test-tenant"
    config = {"provider": "openai", "model": "gpt-4o"}

    # Act
    result = await gateway.generate(
        tenant_id=tenant_id,
        messages=[{"role": "user", "content": "test"}],
        config=config,
    )

    # Assert
    assert result["provider"] == "openai"
    assert "choices" in result
```

### Test Coverage

- Aim for >80% code coverage
- Test happy paths and error cases
- Test edge cases and boundary conditions
- Use fixtures for common setup

```python
@pytest.fixture
async def mock_tenant():
    """Provide a mock tenant for testing."""
    return {
        "id": "test-tenant",
        "name": "Test Corporation",
        "enabled_use_cases": ["support"],
    }

@pytest.fixture
async def llm_gateway(mock_tenant):
    """Provide a configured LLM gateway."""
    gateway = LLMGateway()
    await gateway.initialize()
    return gateway
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/test_llm_gateway.py -v

# Run with coverage
make test-cov

# Run tests matching a pattern
uv run pytest -k "test_gateway" -v
```

## Documentation

### Updating Documentation

- Update relevant documentation when changing functionality
- Add docstrings to all public APIs
- Include usage examples for new features
- Update README.md if adding new capabilities
- Add entries to CHANGELOG.md

### Documentation Structure

```
docs/
├── architecture-overview.md
├── mcp-architecture.md
├── crewai-agents-crews.md
├── langflow-flows.md
├── governance-watsonx.md
└── use-cases/
    ├── support.md
    ├── hr.md
    └── ...
```

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run quality checks**:
   ```bash
   make ci
   ```

3. **Update documentation** if needed

4. **Add tests** for new features

### Submitting a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what and why
   - Link to related issues
   - Screenshots/examples if applicable

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   How has this been tested?

   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] All tests pass
   - [ ] No new warnings
   ```

### Review Process

- At least one maintainer review required
- Address review feedback promptly
- Keep discussions focused and constructive
- Be patient - reviews take time

### After Merge

1. **Delete your branch**:
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Sync your fork**:
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

## Release Process

Releases follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Bumping

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create a git tag:
   ```bash
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push upstream v1.2.0
   ```

## Questions or Issues?

- Open an [issue](https://github.com/ruslanmv/universal-copilot-platform/issues)
- Check existing [discussions](https://github.com/ruslanmv/universal-copilot-platform/discussions)
- Visit [ruslanmv.com](https://ruslanmv.com) for professional support

Thank you for contributing to Universal Copilot Platform!
