"""Tests for the CinderClient."""

import pytest
import respx
from httpx import Response

from cinder import CinderClient
from cinder.generated.models import (
    DecisionSchema,
    PagedDecisionSchema,
    PagedReport,
    Report,
    SchemaResponse,
)


@pytest.fixture
def client():
    """Create a test client instance."""
    return CinderClient(base_url="https://api.example.com", token="test-token")


@pytest.fixture
def sample_decision():
    """Sample decision data."""
    return {
        "uuid": "abc-123",
        "user": "reviewer@example.com",
        "queue_slug": "default",
        "job_id": "job-456",
        "applied_policies": [],
        "applied_actions": ["warn"],
        "entity": {"entity_type": "user", "attributes": {"id": "u1"}},
        "entity_slug": "user",
        "entity_id": "u1",
        "handle_time_seconds": 30,
        "resolution_time_seconds": 60,
        "notes": "Looks fine",
        "is_training": False,
        "previous_decision_id": None,
        "next_decision_id": None,
        "form_submissions": None,
        "created_at": "2025-01-01T00:00:00Z",
        "decision_type": "queue_review",
        "job_assigned_at": None,
        "typed_metadata": None,
    }


@pytest.fixture
def sample_report():
    """Sample report data."""
    return {
        "reasoning": "Spam content",
        "created_at": "2025-01-01T00:00:00Z",
        "metadata": {"source": "auto"},
        "entity": {"entity_schema": "message", "attributes": {"id": "msg-1"}},
        "reporter": {"entity_schema": "user", "attributes": {"id": "u1"}},
        "attribute_slugs": ["body"],
    }


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
                        "attribute_sub_type": None,
                    },
                    {
                        "slug": "email",
                        "label": "Email",
                        "attribute_type": "string",
                        "attribute_sub_type": None,
                    },
                ],
                "title_attribute": {
                    "slug": "username",
                    "label": "Username",
                    "attribute_type": "string",
                    "attribute_sub_type": None,
                },
            },
            {
                "slug": "post",
                "label": "Post",
                "attribute_schemas": [
                    {
                        "slug": "title",
                        "label": "Title",
                        "attribute_type": "string",
                        "attribute_sub_type": None,
                    },
                    {
                        "slug": "content",
                        "label": "Content",
                        "attribute_type": "text",
                        "attribute_sub_type": None,
                    },
                ],
                "title_attribute": {
                    "slug": "title",
                    "label": "Title",
                    "attribute_type": "string",
                    "attribute_sub_type": None,
                },
            },
        ],
        "relationship_schemas": [
            {
                "slug": "authored",
                "label": "Authored",
                "reverse_label": "Authored by",
                "entity_pairs_by_slug": [{"source_slug": "user", "target_slug": "post"}],
            }
        ],
    }


@pytest.fixture
def empty_schema_response():
    """Empty schema response data."""
    return {"entity_schemas": [], "relationship_schemas": []}


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
            return_value=Response(
                200, json={"entity_schemas": [], "relationship_schemas": []}
            )
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
    async def test_get_graph_schema_attribute_details(
        self, client, sample_schema_response
    ):
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


class TestGetDecision:
    """Tests for the get_decision method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_decision_success(self, client, sample_decision):
        """Test successful retrieval of a single decision."""
        route = respx.get("https://api.example.com/api/v1/decisions/abc-123/").mock(
            return_value=Response(200, json=sample_decision)
        )

        async with client:
            decision = await client.get_decision("abc-123")

        assert route.called
        assert isinstance(decision, DecisionSchema)
        assert decision.uuid == "abc-123"
        assert decision.user == "reviewer@example.com"
        assert decision.entity.entity_type == "user"
        assert decision.notes == "Looks fine"
        assert decision.is_training is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_decision_not_found(self, client):
        """Test handling of 404 when decision does not exist."""
        respx.get("https://api.example.com/api/v1/decisions/nonexistent/").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.get_decision("nonexistent")

            assert "404" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_decision_with_auth_header(self, client, sample_decision):
        """Test that authorization header is sent correctly."""
        route = respx.get("https://api.example.com/api/v1/decisions/abc-123/").mock(
            return_value=Response(200, json=sample_decision)
        )

        async with client:
            await client.get_decision("abc-123")

        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer test-token"


class TestListDecisions:
    """Tests for the list_decisions method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_decisions_success(self, client, sample_decision):
        """Test successful retrieval of paginated decisions."""
        paged = {"items": [sample_decision], "count": 1}
        route = respx.get("https://api.example.com/api/v1/decisions/").mock(
            return_value=Response(200, json=paged)
        )

        async with client:
            result = await client.list_decisions()

        assert route.called
        assert isinstance(result, PagedDecisionSchema)
        assert result.count == 1
        assert len(result.items) == 1
        assert result.items[0].uuid == "abc-123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_decisions_with_pagination(self, client, sample_decision):
        """Test that limit and offset are sent as query parameters."""
        paged = {"items": [sample_decision], "count": 50}
        route = respx.get("https://api.example.com/api/v1/decisions/").mock(
            return_value=Response(200, json=paged)
        )

        async with client:
            await client.list_decisions(limit=10, offset=20)

        request = route.calls.last.request
        assert "limit=10" in str(request.url)
        assert "offset=20" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_decisions_with_filters(self, client, sample_decision):
        """Test that filters are sent as query parameters."""
        from cinder.generated.models import DecisionFilter

        paged = {"items": [sample_decision], "count": 1}
        route = respx.get("https://api.example.com/api/v1/decisions/").mock(
            return_value=Response(200, json=paged)
        )

        filters = DecisionFilter(queue="default", entity_id="u1")
        async with client:
            await client.list_decisions(filters=filters)

        request = route.calls.last.request
        assert "queue=default" in str(request.url)
        assert "entity_id=u1" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_decisions_empty(self, client):
        """Test retrieval of empty decision list."""
        paged = {"items": [], "count": 0}
        route = respx.get("https://api.example.com/api/v1/decisions/").mock(
            return_value=Response(200, json=paged)
        )

        async with client:
            result = await client.list_decisions()

        assert route.called
        assert isinstance(result, PagedDecisionSchema)
        assert result.count == 0
        assert len(result.items) == 0


class TestGetDecisionReports:
    """Tests for the get_decision_reports method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_decision_reports_success(self, client, sample_report):
        """Test successful retrieval of reports for a decision."""
        route = respx.get(
            "https://api.example.com/api/v2/decisions/abc-123/reports/"
        ).mock(return_value=Response(200, json=[sample_report]))

        async with client:
            reports = await client.get_decision_reports("abc-123")

        assert route.called
        assert len(reports) == 1
        assert isinstance(reports[0], Report)
        assert reports[0].reasoning == "Spam content"
        assert reports[0].entity.entity_schema == "message"
        assert reports[0].reporter.entity_schema == "user"
        assert reports[0].attribute_slugs == ["body"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_decision_reports_empty(self, client):
        """Test retrieval when decision has no reports."""
        route = respx.get(
            "https://api.example.com/api/v2/decisions/abc-123/reports/"
        ).mock(return_value=Response(200, json=[]))

        async with client:
            reports = await client.get_decision_reports("abc-123")

        assert route.called
        assert reports == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_decision_reports_not_found(self, client):
        """Test handling of 404 when decision does not exist."""
        respx.get(
            "https://api.example.com/api/v2/decisions/nonexistent/reports/"
        ).mock(return_value=Response(404, json={"detail": "Not found"}))

        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.get_decision_reports("nonexistent")

            assert "404" in str(exc_info.value)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_decision_reports_with_auth_header(self, client, sample_report):
        """Test that authorization header is sent correctly."""
        route = respx.get(
            "https://api.example.com/api/v2/decisions/abc-123/reports/"
        ).mock(return_value=Response(200, json=[sample_report]))

        async with client:
            await client.get_decision_reports("abc-123")

        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer test-token"


class TestListReports:
    """Tests for the list_reports method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_reports_success(self, client, sample_report):
        """Test successful retrieval of paginated reports."""
        paged = {"items": [sample_report], "count": 1}
        route = respx.get("https://api.example.com/api/v1/report/").mock(
            return_value=Response(200, json=paged)
        )

        async with client:
            result = await client.list_reports()

        assert route.called
        assert isinstance(result, PagedReport)
        assert result.count == 1
        assert len(result.items) == 1
        assert isinstance(result.items[0], Report)
        assert result.items[0].reasoning == "Spam content"

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_reports_with_pagination(self, client, sample_report):
        """Test that limit and offset are sent as query parameters."""
        paged = {"items": [sample_report], "count": 50}
        route = respx.get("https://api.example.com/api/v1/report/").mock(
            return_value=Response(200, json=paged)
        )

        async with client:
            await client.list_reports(limit=10, offset=20)

        request = route.calls.last.request
        assert "limit=10" in str(request.url)
        assert "offset=20" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_reports_empty(self, client):
        """Test retrieval of empty report list."""
        paged = {"items": [], "count": 0}
        route = respx.get("https://api.example.com/api/v1/report/").mock(
            return_value=Response(200, json=paged)
        )

        async with client:
            result = await client.list_reports()

        assert route.called
        assert isinstance(result, PagedReport)
        assert result.count == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_reports_with_auth_header(self, client, sample_report):
        """Test that authorization header is sent correctly."""
        paged = {"items": [sample_report], "count": 1}
        route = respx.get("https://api.example.com/api/v1/report/").mock(
            return_value=Response(200, json=paged)
        )

        async with client:
            await client.list_reports()

        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer test-token"
