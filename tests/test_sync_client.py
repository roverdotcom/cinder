"""Tests for the SyncCinderClient."""
import pytest
import respx
from httpx import Response

from cinder import SyncCinderClient
from cinder.generated.models import SchemaResponse


@pytest.fixture
def client():
    """Create a test sync client instance."""
    return SyncCinderClient(
        base_url="https://api.example.com",
        token="test-token"
    )


@pytest.fixture
def sample_schema_response():
    """Sample schema response data."""
    return {
        "entity_schemas": [
            {
                "slug": "user",
                "label": "User",
                "attribute_schemas": [
                    {
                        "slug": "username",
                        "label": "Username",
                        "attribute_type": "string",
                        "attribute_sub_type": None
                    }
                ],
                "title_attribute": {
                    "slug": "username",
                    "label": "Username",
                    "attribute_type": "string",
                    "attribute_sub_type": None
                }
            }
        ],
        "relationship_schemas": []
    }


class TestSyncGetGraphSchema:
    """Tests for the synchronous get_graph_schema method."""

    @respx.mock
    def test_get_graph_schema_success(self, client, sample_schema_response):
        """Test successful retrieval of graph schema."""
        # Mock the API endpoint
        route = respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(200, json=sample_schema_response)
        )

        # Call the method
        with client:
            schema = client.get_graph_schema()

        # Verify the request was made
        assert route.called
        assert route.call_count == 1

        # Verify the response type
        assert isinstance(schema, SchemaResponse)
        assert len(schema.entity_schemas) == 1
        assert schema.entity_schemas[0].slug == "user"

    @respx.mock
    def test_get_graph_schema_with_auth_header(self, client):
        """Test that authorization header is sent correctly."""
        route = respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(200, json={
                "entity_schemas": [],
                "relationship_schemas": []
            })
        )

        with client:
            client.get_graph_schema()

        # Verify the Authorization header was sent
        assert route.called
        request = route.calls.last.request
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == "Bearer test-token"

    @respx.mock
    def test_get_graph_schema_error_handling(self, client):
        """Test handling of API errors."""
        respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(403, json={"error": "Forbidden"})
        )

        with client:
            with pytest.raises(Exception) as exc_info:
                client.get_graph_schema()

            assert "403" in str(exc_info.value)

    @respx.mock
    def test_context_manager(self, client, sample_schema_response):
        """Test that context manager properly opens and closes the client."""
        respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(200, json=sample_schema_response)
        )

        # Use context manager
        with client:
            schema = client.get_graph_schema()
            assert isinstance(schema, SchemaResponse)

        # After exiting context, client should be closed
        # Note: httpx.Client doesn't have an explicit "closed" attribute,
        # but we can verify it doesn't raise an error

    def test_manual_close(self, client):
        """Test manual close method."""
        # Should not raise an error
        client.close()
