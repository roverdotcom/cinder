"""Tests for the CinderClient."""
import pytest
import respx
from httpx import Response

from cinder import CinderClient
from cinder.generated.models import SchemaResponse


@pytest.fixture
def client():
    """Create a test client instance."""
    return CinderClient(
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
                    },
                    {
                        "slug": "email",
                        "label": "Email",
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
            },
            {
                "slug": "post",
                "label": "Post",
                "attribute_schemas": [
                    {
                        "slug": "title",
                        "label": "Title",
                        "attribute_type": "string",
                        "attribute_sub_type": None
                    },
                    {
                        "slug": "content",
                        "label": "Content",
                        "attribute_type": "text",
                        "attribute_sub_type": None
                    }
                ],
                "title_attribute": {
                    "slug": "title",
                    "label": "Title",
                    "attribute_type": "string",
                    "attribute_sub_type": None
                }
            }
        ],
        "relationship_schemas": [
            {
                "slug": "authored",
                "label": "Authored",
                "reverse_label": "Authored by",
                "entity_pairs_by_slug": [
                    {
                        "source_slug": "user",
                        "target_slug": "post"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def empty_schema_response():
    """Empty schema response data."""
    return {
        "entity_schemas": [],
        "relationship_schemas": []
    }


class TestGetGraphSchema:
    """Tests for the get_graph_schema method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_graph_schema_success(self, client, sample_schema_response):
        """Test successful retrieval of graph schema."""
        # Mock the API endpoint
        route = respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(200, json=sample_schema_response)
        )

        # Call the method
        async with client:
            schema = await client.get_graph_schema()

        # Verify the request was made
        assert route.called
        assert route.call_count == 1

        # Verify the response type
        assert isinstance(schema, SchemaResponse)

        # Verify entity schemas
        assert len(schema.entity_schemas) == 2
        assert schema.entity_schemas[0].slug == "user"
        assert schema.entity_schemas[0].label == "User"
        assert len(schema.entity_schemas[0].attribute_schemas) == 2
        assert schema.entity_schemas[1].slug == "post"
        assert schema.entity_schemas[1].label == "Post"

        # Verify relationship schemas
        assert len(schema.relationship_schemas) == 1
        assert schema.relationship_schemas[0].slug == "authored"
        assert schema.relationship_schemas[0].label == "Authored"
        assert schema.relationship_schemas[0].reverse_label == "Authored by"
        assert len(schema.relationship_schemas[0].entity_pairs_by_slug) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_graph_schema_empty(self, client, empty_schema_response):
        """Test retrieval of empty graph schema."""
        # Mock the API endpoint with empty schema
        route = respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(200, json=empty_schema_response)
        )

        # Call the method
        async with client:
            schema = await client.get_graph_schema()

        # Verify the request was made
        assert route.called

        # Verify empty schema
        assert isinstance(schema, SchemaResponse)
        assert len(schema.entity_schemas) == 0
        assert len(schema.relationship_schemas) == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_graph_schema_unauthorized(self, client):
        """Test handling of 403 Forbidden response."""
        # Mock the API endpoint with 403 error
        respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(403, json={"error": "Forbidden"})
        )

        # Verify that HTTPStatusError is raised
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.get_graph_schema()

            # httpx raises HTTPStatusError for 4xx/5xx responses
            assert "403" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_graph_schema_server_error(self, client):
        """Test handling of 500 Internal Server Error response."""
        # Mock the API endpoint with 500 error
        respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(500, json={"error": "Internal Server Error"})
        )

        # Verify that HTTPStatusError is raised
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.get_graph_schema()

            assert "500" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_graph_schema_network_error(self, client):
        """Test handling of network errors."""
        # Mock the API endpoint to raise a connection error
        from httpx import ConnectError

        respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            side_effect=ConnectError("Connection failed")
        )

        # Verify that ConnectError is raised
        async with client:
            with pytest.raises(ConnectError):
                await client.get_graph_schema()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_graph_schema_validates_response(self, client):
        """Test that invalid response data raises validation error."""
        # Mock the API endpoint with invalid data (missing required fields)
        respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(200, json={"invalid": "data"})
        )

        # Verify that validation error is raised
        async with client:
            with pytest.raises(Exception):  # Pydantic ValidationError
                await client.get_graph_schema()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_graph_schema_with_auth_header(self, client):
        """Test that authorization header is sent correctly."""
        route = respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(200, json={
                "entity_schemas": [],
                "relationship_schemas": []
            })
        )

        async with client:
            await client.get_graph_schema()

        # Verify the Authorization header was sent
        assert route.called
        request = route.calls.last.request
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_graph_schema_attribute_details(self, client, sample_schema_response):
        """Test detailed attribute schema parsing."""
        respx.get("https://api.example.com/api/v1/graph/schema/").mock(
            return_value=Response(200, json=sample_schema_response)
        )

        async with client:
            schema = await client.get_graph_schema()

        # Verify attribute details
        user_schema = schema.entity_schemas[0]
        assert user_schema.title_attribute is not None
        assert user_schema.title_attribute.slug == "username"

        username_attr = user_schema.attribute_schemas[0]
        assert username_attr.slug == "username"
        assert username_attr.label == "Username"
        assert username_attr.attribute_type == "string"
        assert username_attr.attribute_sub_type is None
