"""Example LLM gateway tests.

This module demonstrates best practices for testing async LLM integrations,
mocking external APIs, and handling provider failures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest

if TYPE_CHECKING:
    from backend.universal_copilot.llm.gateway import LLMGateway


class TestLLMGateway:
    """Test suite for LLM gateway functionality."""

    @pytest.fixture
    async def llm_gateway(self, mocker):
        """Provide an LLM gateway instance with mocked dependencies.

        Args:
            mocker: Pytest-mock fixture.

        Returns:
            LLMGateway instance.
        """
        # Import here to avoid circular dependencies
        from backend.universal_copilot.llm.gateway import LLMGateway

        # Mock settings to avoid requiring real API keys
        mock_settings = mocker.patch(
            "backend.universal_copilot.llm.gateway.settings"
        )
        mock_settings.openai_api_key = "test-key"
        mock_settings.anthropic_api_key = "test-key"

        return LLMGateway()

    @pytest.fixture
    def sample_messages(self) -> list[dict]:
        """Provide sample chat messages.

        Returns:
            List of chat messages.
        """
        return [
            {"role": "user", "content": "What is the capital of France?"}
        ]

    @pytest.mark.asyncio
    async def test_generate_with_openai_provider(
        self,
        llm_gateway,
        sample_messages: list[dict],
        mocker,
    ) -> None:
        """Test LLM generation with OpenAI provider.

        Args:
            llm_gateway: LLM gateway fixture.
            sample_messages: Sample messages fixture.
            mocker: Pytest-mock fixture.
        """
        # Arrange - mock OpenAI client
        mock_response = {
            "id": "chatcmpl-test",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "The capital of France is Paris.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 8,
                "total_tokens": 18,
            },
        }

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mocker.patch.object(llm_gateway, "_get_openai_client", return_value=mock_client)

        # Act
        result = await llm_gateway.generate(
            provider="openai",
            model="gpt-4o",
            messages=sample_messages,
        )

        # Assert
        assert result is not None
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert result["choices"][0]["message"]["content"] == "The capital of France is Paris."

    @pytest.mark.asyncio
    async def test_generate_with_streaming(
        self,
        llm_gateway,
        sample_messages: list[dict],
        mocker,
    ) -> None:
        """Test streaming LLM generation.

        Args:
            llm_gateway: LLM gateway fixture.
            sample_messages: Sample messages fixture.
            mocker: Pytest-mock fixture.
        """
        # Arrange - mock streaming response
        async def mock_stream():
            chunks = [
                {"delta": {"content": "The "}},
                {"delta": {"content": "capital "}},
                {"delta": {"content": "is Paris."}},
                {"delta": {}, "finish_reason": "stop"},
            ]
            for chunk in chunks:
                yield chunk

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_stream()
        mocker.patch.object(llm_gateway, "_get_openai_client", return_value=mock_client)

        # Act
        chunks = []
        async for chunk in llm_gateway.generate_stream(
            provider="openai",
            model="gpt-4o",
            messages=sample_messages,
        ):
            chunks.append(chunk)

        # Assert
        assert len(chunks) > 0
        # Reconstruct full response from chunks
        full_text = "".join(
            chunk.get("delta", {}).get("content", "")
            for chunk in chunks
        )
        assert "Paris" in full_text

    @pytest.mark.asyncio
    async def test_provider_fallback_on_error(
        self,
        llm_gateway,
        sample_messages: list[dict],
        mocker,
    ) -> None:
        """Test automatic fallback to secondary provider on primary failure.

        Args:
            llm_gateway: LLM gateway fixture.
            sample_messages: Sample messages fixture.
            mocker: Pytest-mock fixture.
        """
        # Arrange - primary provider fails
        mock_openai = AsyncMock()
        mock_openai.chat.completions.create.side_effect = Exception("Rate limit exceeded")

        # Secondary provider succeeds
        mock_anthropic = AsyncMock()
        mock_anthropic.messages.create.return_value = {
            "content": [{"text": "Paris is the capital."}],
            "usage": {"input_tokens": 10, "output_tokens": 8},
        }

        mocker.patch.object(llm_gateway, "_get_openai_client", return_value=mock_openai)
        mocker.patch.object(llm_gateway, "_get_anthropic_client", return_value=mock_anthropic)

        # Act
        result = await llm_gateway.generate_with_fallback(
            primary_provider="openai",
            fallback_provider="anthropic",
            model="gpt-4o",
            messages=sample_messages,
        )

        # Assert
        assert result is not None
        assert "content" in result
        assert "Paris" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self,
        llm_gateway,
        sample_messages: list[dict],
        mocker,
    ) -> None:
        """Test handling multiple concurrent LLM requests.

        Args:
            llm_gateway: LLM gateway fixture.
            sample_messages: Sample messages fixture.
            mocker: Pytest-mock fixture.
        """
        # Arrange
        import asyncio

        mock_response = {
            "id": "chatcmpl-test",
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Test response"},
                    "finish_reason": "stop",
                }
            ],
        }

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mocker.patch.object(llm_gateway, "_get_openai_client", return_value=mock_client)

        # Act - make 10 concurrent requests
        tasks = [
            llm_gateway.generate(
                provider="openai",
                model="gpt-4o",
                messages=sample_messages,
            )
            for _ in range(10)
        ]
        results = await asyncio.gather(*tasks)

        # Assert
        assert len(results) == 10
        assert all(r is not None for r in results)
        assert all("choices" in r for r in results)


class TestTokenCounting:
    """Test suite for token counting and cost tracking."""

    @pytest.fixture
    def token_counter(self):
        """Provide a token counter instance.

        Returns:
            TokenCounter instance.
        """
        from backend.universal_copilot.llm.token_counter import TokenCounter

        return TokenCounter()

    def test_count_tokens_for_message(self, token_counter) -> None:
        """Test token counting for a message.

        Args:
            token_counter: Token counter fixture.
        """
        # Arrange
        message = "What is the capital of France?"

        # Act
        token_count = token_counter.count_tokens(message, model="gpt-4o")

        # Assert
        assert token_count > 0
        assert token_count < 100  # Reasonable upper bound for this short message

    def test_calculate_cost(self, token_counter) -> None:
        """Test cost calculation based on token usage.

        Args:
            token_counter: Token counter fixture.
        """
        # Arrange
        usage = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }

        # Act
        cost = token_counter.calculate_cost(
            usage=usage,
            model="gpt-4o",
            provider="openai",
        )

        # Assert
        assert cost > 0
        assert isinstance(cost, (int, float))

    def test_token_limit_enforcement(self, token_counter) -> None:
        """Test that token limits are enforced.

        Args:
            token_counter: Token counter fixture.
        """
        # Arrange
        max_tokens = 1000
        message = "test " * 500  # Very long message

        # Act
        token_count = token_counter.count_tokens(message, model="gpt-4o")
        exceeds_limit = token_count > max_tokens

        # Assert
        if exceeds_limit:
            # Should raise or truncate
            assert token_count > max_tokens
        else:
            assert token_count <= max_tokens


class TestRetryLogic:
    """Test suite for retry logic on transient failures."""

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self, mocker) -> None:
        """Test that transient errors trigger retry.

        Args:
            mocker: Pytest-mock fixture.
        """
        # Arrange
        from backend.universal_copilot.llm.gateway import LLMGateway

        gateway = LLMGateway()

        # Mock: fail twice, succeed on third attempt
        call_count = 0

        async def mock_api_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary network error")
            return {"choices": [{"message": {"content": "Success"}}]}

        mocker.patch.object(
            gateway,
            "_make_api_call",
            side_effect=mock_api_call,
        )

        # Act
        result = await gateway.generate_with_retry(
            provider="openai",
            model="gpt-4o",
            messages=[{"role": "user", "content": "test"}],
            max_retries=3,
        )

        # Assert
        assert call_count == 3  # Failed twice, succeeded on third
        assert result is not None

    @pytest.mark.asyncio
    async def test_no_retry_on_validation_error(self, mocker) -> None:
        """Test that validation errors do NOT trigger retry.

        Args:
            mocker: Pytest-mock fixture.
        """
        # Arrange
        from backend.universal_copilot.llm.gateway import LLMGateway

        gateway = LLMGateway()
        call_count = 0

        async def mock_api_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid input")

        mocker.patch.object(
            gateway,
            "_make_api_call",
            side_effect=mock_api_call,
        )

        # Act & Assert
        with pytest.raises(ValueError):
            await gateway.generate_with_retry(
                provider="openai",
                model="gpt-4o",
                messages=[{"role": "user", "content": "test"}],
                max_retries=3,
            )

        # Should only call once (no retry on validation errors)
        assert call_count == 1
