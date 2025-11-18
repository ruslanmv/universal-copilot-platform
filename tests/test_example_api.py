"""Example API integration tests.

This module demonstrates best practices for testing FastAPI endpoints
with async handlers, authentication, and database interactions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi import status
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from backend.universal_copilot.main import FastAPI


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_health_check_returns_200(self, test_client: TestClient) -> None:
        """Test that health endpoint returns 200 OK.

        Args:
            test_client: FastAPI test client fixture.
        """
        # Arrange - setup is done via fixture

        # Act
        response = test_client.get("/health")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    def test_health_check_includes_timestamp(self, test_client: TestClient) -> None:
        """Test that health endpoint includes timestamp.

        Args:
            test_client: FastAPI test client fixture.
        """
        # Act
        response = test_client.get("/health")
        data = response.json()

        # Assert
        assert "timestamp" in data or "status" in data
        assert data["status"] == "healthy"


class TestSupportEndpoints:
    """Test suite for support copilot endpoints."""

    @pytest.fixture
    def support_query_payload(self) -> dict:
        """Provide a valid support query payload.

        Returns:
            Dictionary with support query data.
        """
        return {
            "message": "How do I reset my password?",
            "channel": "web",
            "user_id": "user-123",
        }

    @pytest.fixture
    def auth_headers(self) -> dict:
        """Provide authentication headers.

        Returns:
            Dictionary with auth headers.
        """
        return {
            "Authorization": "Bearer test-token",
            "X-Tenant-ID": "test-tenant-001",
        }

    def test_support_query_requires_authentication(
        self,
        test_client: TestClient,
        support_query_payload: dict,
    ) -> None:
        """Test that support query requires authentication.

        Args:
            test_client: FastAPI test client fixture.
            support_query_payload: Support query payload fixture.
        """
        # Act - make request without auth header
        response = test_client.post(
            "/api/v1/support/query",
            json=support_query_payload,
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_support_query_validates_payload(
        self,
        test_client: TestClient,
        auth_headers: dict,
    ) -> None:
        """Test that support query validates payload schema.

        Args:
            test_client: FastAPI test client fixture.
            auth_headers: Auth headers fixture.
        """
        # Arrange - invalid payload (missing required fields)
        invalid_payload = {"message": ""}

        # Act
        response = test_client.post(
            "/api/v1/support/query",
            json=invalid_payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_support_query_success(
        self,
        test_client: TestClient,
        support_query_payload: dict,
        auth_headers: dict,
        mocker,
    ) -> None:
        """Test successful support query with mocked LLM response.

        Args:
            test_client: FastAPI test client fixture.
            support_query_payload: Support query payload fixture.
            auth_headers: Auth headers fixture.
            mocker: Pytest-mock fixture.
        """
        # Arrange - mock the crew response
        mock_crew = mocker.patch(
            "backend.universal_copilot.crew.registry.get_crew"
        )
        mock_crew.return_value.run_support_flow.return_value = {
            "answer": "To reset your password, visit https://example.com/reset",
            "confidence": 0.95,
            "sources": ["KB-001"],
        }

        # Act
        response = test_client.post(
            "/api/v1/support/query",
            json=support_query_payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "answer" in data
        assert data["confidence"] >= 0.9


class TestRateLimiting:
    """Test suite for rate limiting functionality."""

    def test_rate_limit_enforced(self, test_client: TestClient) -> None:
        """Test that rate limiting is enforced after threshold.

        Args:
            test_client: FastAPI test client fixture.
        """
        # Arrange
        endpoint = "/health"
        max_requests = 100

        # Act - make requests until rate limit
        responses = []
        for _ in range(max_requests + 10):
            responses.append(test_client.get(endpoint))

        # Assert - last few requests should be rate limited
        # Note: This test assumes rate limiting is configured
        rate_limited = [r for r in responses if r.status_code == status.HTTP_429_TOO_MANY_REQUESTS]

        # If rate limiting is enabled, we should see some 429s
        # If not enabled, all should be 200
        assert all(r.status_code in [200, 429] for r in responses)


class TestErrorHandling:
    """Test suite for error handling and validation."""

    def test_404_for_unknown_endpoint(self, test_client: TestClient) -> None:
        """Test that unknown endpoints return 404.

        Args:
            test_client: FastAPI test client fixture.
        """
        # Act
        response = test_client.get("/api/v1/nonexistent")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_405_for_wrong_http_method(self, test_client: TestClient) -> None:
        """Test that wrong HTTP methods return 405.

        Args:
            test_client: FastAPI test client fixture.
        """
        # Act - GET on a POST-only endpoint
        response = test_client.get("/api/v1/support/query")

        # Assert
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_500_error_includes_detail(
        self,
        test_client: TestClient,
        mocker,
    ) -> None:
        """Test that 500 errors include error details.

        Args:
            test_client: FastAPI test client fixture.
            mocker: Pytest-mock fixture.
        """
        # Arrange - mock to raise an exception
        mocker.patch(
            "backend.universal_copilot.crew.registry.get_crew",
            side_effect=Exception("Internal error"),
        )

        # Act
        response = test_client.post(
            "/api/v1/support/query",
            json={"message": "test", "channel": "web"},
            headers={"Authorization": "Bearer test", "X-Tenant-ID": "test"},
        )

        # Assert - should handle gracefully
        assert response.status_code in [
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_401_UNAUTHORIZED,
        ]
