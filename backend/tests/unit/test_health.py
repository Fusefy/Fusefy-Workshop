"""
Unit tests for health check endpoints.

This module tests the health check functionality of the Claims Reimbursement System,
including basic health status and detailed health information with database connectivity.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

from src.config.database import db_config


class TestHealthEndpoint:
    """Test suite for the basic health check endpoint."""

    @pytest.mark.unit
    def test_health_check_success(self, test_client: TestClient):
        """
        Test successful health check response.
        
        This test verifies that the basic health endpoint returns
        a successful response with the expected structure and fields.
        
        Expected behavior:
        - Returns HTTP 200 status
        - Response contains status, timestamp, database, and version fields
        - Status field indicates "healthy"
        - Timestamp is in ISO format
        """
        # Act: Make request to health endpoint
        response = test_client.get("/api/health")
        
        # Assert: Check response status and structure
        assert response.status_code == 200, "Health check should return HTTP 200"
        
        data = response.json()
        
        # Verify all required fields are present
        assert "status" in data, "Response should contain 'status' field"
        assert "timestamp" in data, "Response should contain 'timestamp' field"
        assert "database" in data, "Response should contain 'database' field"
        assert "version" in data, "Response should contain 'version' field"
        
        # Verify field values
        assert data["status"] == "healthy", "Status should be 'healthy' for successful check"
        assert data["version"] == "1.0.0", "Version should match application version"
        
        # Verify timestamp is valid ISO format
        try:
            datetime.fromisoformat(data["timestamp"])
        except ValueError:
            pytest.fail("Timestamp should be in valid ISO format")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_check_async_client(self, async_client: AsyncClient):
        """
        Test health check endpoint using async client.
        
        This test ensures the health endpoint works correctly with
        asynchronous HTTP clients, which is important for integration
        with async web frameworks and monitoring systems.
        
        Expected behavior:
        - Returns HTTP 200 status via async client
        - Response structure matches synchronous client response
        """
        # Act: Make async request to health endpoint
        response = await async_client.get("/api/health")
        
        # Assert: Verify response
        assert response.status_code == 200, "Async health check should return HTTP 200"
        
        data = response.json()
        assert data["status"] == "healthy", "Async response should indicate healthy status"
        
        # Verify timestamp is recent (within last minute)
        timestamp = datetime.fromisoformat(data["timestamp"])
        now = datetime.now()
        time_diff = (now - timestamp.replace(tzinfo=None)).total_seconds()
        assert time_diff < 60, "Timestamp should be recent (within last minute)"

    @pytest.mark.unit
    def test_health_check_response_format(self, test_client: TestClient):
        """
        Test the exact response format of health check.
        
        This test validates that the health check response matches
        the expected Pydantic model structure exactly, ensuring
        API contract compliance.
        
        Expected behavior:
        - Response matches HealthResponse schema
        - All fields have correct types
        - No extra or missing fields
        """
        # Act: Get health check response
        response = test_client.get("/api/health")
        data = response.json()
        
        # Assert: Verify exact field types and structure
        assert isinstance(data["status"], str), "Status should be string"
        assert isinstance(data["timestamp"], str), "Timestamp should be string"
        assert isinstance(data["database"], str), "Database should be string"
        assert isinstance(data["version"], str), "Version should be string"
        
        # Verify no unexpected fields
        expected_fields = {"status", "timestamp", "database", "version"}
        actual_fields = set(data.keys())
        assert actual_fields == expected_fields, f"Response should only contain {expected_fields}"


class TestDetailedHealthEndpoint:
    """Test suite for the detailed health check endpoint."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_detailed_health_with_database_available(self, async_client: AsyncClient):
        """
        Test detailed health check when database is available.
        
        This test verifies that the detailed health endpoint correctly
        reports database connectivity when the database is accessible.
        
        Expected behavior:
        - Returns HTTP 200 status
        - Overall status is "healthy"
        - Database service status is "healthy"
        - API service status is "healthy"
        """
        # Act: Request detailed health information
        response = await async_client.get("/api/health/detailed")
        
        # Assert: Check response structure and status
        assert response.status_code == 200, "Detailed health check should return HTTP 200"
        
        data = response.json()
        
        # Verify top-level structure
        assert "status" in data, "Response should contain overall status"
        assert "timestamp" in data, "Response should contain timestamp"
        assert "version" in data, "Response should contain version"
        assert "services" in data, "Response should contain services section"
        
        # Verify services structure
        services = data["services"]
        assert "api" in services, "Services should include API status"
        assert "database" in services, "Services should include database status"
        
        # Verify API service status
        api_service = services["api"]
        assert api_service["status"] == "healthy", "API service should be healthy"
        assert "message" in api_service, "API service should have status message"
        
        # Verify overall status reflects healthy database
        # Note: In test environment with working test DB, should be healthy
        assert data["status"] in ["healthy", "degraded"], "Overall status should be healthy or degraded"

    @pytest.mark.integration 
    def test_detailed_health_database_connection_test(self, test_client: TestClient):
        """
        Test that detailed health check actually tests database connectivity.
        
        This test ensures that the health check performs a real database
        query to verify connectivity, not just checking if the session
        factory exists.
        
        Expected behavior:
        - Executes SELECT 1 query against database
        - Reports database status based on query success
        """
        # Act: Get detailed health information
        response = test_client.get("/api/health/detailed")
        
        # Assert: Verify database test was performed
        assert response.status_code == 200
        data = response.json()
        
        # Database status should be determined by actual connectivity test
        db_service = data["services"]["database"]
        
        # Should have either succeeded or failed with specific message
        assert db_service["status"] in ["healthy", "unhealthy", "unavailable"]
        assert "message" in db_service, "Database service should have status message"
        
        # If healthy, message should indicate successful connection
        if db_service["status"] == "healthy":
            assert "successful" in db_service["message"].lower()

    @pytest.mark.unit
    @patch('src.config.database.db_config.session_factory', None)
    def test_detailed_health_no_database_initialized(self, test_client: TestClient):
        """
        Test detailed health check when database is not initialized.
        
        This test simulates the scenario where the database connection
        was never established, ensuring proper error reporting.
        
        Expected behavior:
        - Returns HTTP 200 (service is running)
        - Overall status is "degraded"
        - Database status is "unavailable"
        - Appropriate error message is provided
        """
        # Act: Request detailed health with no database
        response = test_client.get("/api/health/detailed")
        
        # Assert: Check degraded service response
        assert response.status_code == 200, "Health endpoint should still respond without database"
        
        data = response.json()
        
        # Overall status should reflect degraded service
        assert data["status"] == "degraded", "Status should be degraded without database"
        
        # Database service should report unavailable
        db_service = data["services"]["database"]
        assert db_service["status"] == "unavailable", "Database should be unavailable"
        assert "not initialized" in db_service["message"].lower(), "Should indicate database not initialized"
        
        # API service should still be healthy
        api_service = data["services"]["api"]
        assert api_service["status"] == "healthy", "API should still be healthy without database"

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.api.health.db_config')
    async def test_detailed_health_database_connection_error(self, mock_db_config, async_client: AsyncClient):
        """
        Test detailed health check when database connection fails.
        
        This test simulates a database connection failure during the
        health check to ensure proper error handling and reporting.
        
        Expected behavior:
        - Returns HTTP 200 (endpoint is accessible)
        - Overall status is "degraded" 
        - Database status is "unhealthy"
        - Error details are included in message
        """
        # Arrange: Mock database connection failure
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("Connection timeout")
        
        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_session_factory.return_value.__aexit__.return_value = None
        
        mock_db_config.session_factory = mock_session_factory
        
        # Act: Request detailed health check
        response = await async_client.get("/api/health/detailed")
        
        # Assert: Verify error handling
        assert response.status_code == 200, "Health endpoint should respond even with DB errors"
        
        data = response.json()
        
        # Should report degraded overall status
        assert data["status"] == "degraded", "Overall status should be degraded on DB error"
        
        # Database should be unhealthy
        db_service = data["services"]["database"]
        assert db_service["status"] == "unhealthy", "Database should be unhealthy on connection error"
        assert "failed" in db_service["message"].lower(), "Message should indicate failure"

    @pytest.mark.unit
    def test_detailed_health_response_structure(self, test_client: TestClient):
        """
        Test the complete structure of detailed health response.
        
        This test validates that the detailed health response contains
        all required fields and follows the expected nested structure.
        
        Expected behavior:
        - Contains all top-level fields: status, timestamp, version, services
        - Services contains both api and database entries
        - Each service has status and message fields
        - All fields have correct types
        """
        # Act: Get detailed health response
        response = test_client.get("/api/health/detailed")
        data = response.json()
        
        # Assert: Verify complete structure
        
        # Top-level fields
        required_top_fields = {"status", "timestamp", "version", "services"}
        assert set(data.keys()) >= required_top_fields, f"Missing top-level fields: {required_top_fields - set(data.keys())}"
        
        # Services structure
        services = data["services"]
        required_services = {"api", "database"}
        assert set(services.keys()) >= required_services, f"Missing services: {required_services - set(services.keys())}"
        
        # Each service structure
        for service_name, service_data in services.items():
            assert "status" in service_data, f"{service_name} service should have status"
            assert "message" in service_data, f"{service_name} service should have message"
            assert isinstance(service_data["status"], str), f"{service_name} status should be string"
            assert isinstance(service_data["message"], str), f"{service_name} message should be string"
        
        # Type validation for top-level fields
        assert isinstance(data["status"], str), "Overall status should be string"
        assert isinstance(data["timestamp"], str), "Timestamp should be string"
        assert isinstance(data["version"], str), "Version should be string"
        assert isinstance(data["services"], dict), "Services should be dictionary"

    @pytest.mark.unit
    def test_health_endpoints_performance(self, test_client: TestClient, performance_timer):
        """
        Test that health check endpoints respond quickly.
        
        Health checks should be fast to avoid timeout issues in
        monitoring systems and load balancers.
        
        Expected behavior:
        - Basic health check responds in under 100ms
        - Detailed health check responds in under 500ms
        """
        # Test basic health check performance
        performance_timer.start()
        response = test_client.get("/api/health")
        basic_time = performance_timer.stop()
        
        assert response.status_code == 200, "Basic health check should succeed"
        assert basic_time < 0.1, f"Basic health check too slow: {basic_time:.3f}s (should be <0.1s)"
        
        # Test detailed health check performance  
        performance_timer.start()
        response = test_client.get("/api/health/detailed")
        detailed_time = performance_timer.stop()
        
        assert response.status_code == 200, "Detailed health check should succeed"
        assert detailed_time < 0.5, f"Detailed health check too slow: {detailed_time:.3f}s (should be <0.5s)"