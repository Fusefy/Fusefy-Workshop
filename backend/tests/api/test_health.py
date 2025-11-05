"""
API integration tests for health check endpoints.

This module tests the health check functionality through HTTP requests,
verifying the complete request-response cycle for health endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestHealthAPI:
    """Test suite for health check API endpoints."""

    @pytest.mark.integration
    def test_health_check_basic(self, test_client: TestClient):
        """
        Test basic health check endpoint.
        
        Verifies that the health endpoint returns proper status
        and required fields for monitoring purposes.
        """
        # Act: Make request to health endpoint
        response = test_client.get("/api/health")
        
        # Assert: Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "status" in data
        assert "timestamp" in data
        assert "database" in data
        assert "version" in data
        assert data["status"] == "healthy"

    @pytest.mark.integration
    async def test_health_check_async(self, async_client: AsyncClient):
        """
        Test health check with async client.
        
        Verifies async request handling for health endpoints.
        """
        # Act: Make async request to health endpoint
        response = await async_client.get("/api/health")
        
        # Assert: Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify basic structure
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @pytest.mark.integration
    def test_health_detailed_endpoint(self, test_client: TestClient):
        """
        Test detailed health check endpoint.
        
        Verifies that detailed health provides additional
        system information and diagnostics.
        """
        # Act: Make request to detailed health endpoint
        response = test_client.get("/api/health/detailed")
        
        # Assert: Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify detailed fields
        assert "status" in data
        assert "timestamp" in data
        assert "database" in data
        assert "system" in data
        assert "uptime_seconds" in data
        
        # Check system info structure
        system_info = data["system"]
        assert "python_version" in system_info
        assert "platform" in system_info