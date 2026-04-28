"""Tests for the SyncCinderClient."""

import pytest
import respx
from httpx import Response

from cinder import SyncCinderClient
from cinder.generated.models import (
    DecisionSchema,
    PagedDecisionSchema,
    PagedReport,
    Report,
    SchemaResponse,
)


@pytest.fixture
def client():
    """Create a test sync client instance."""
    return SyncCinderClient(base_url="https://api.example.com", token="test-token")


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
                    }
                ],
                "title_attribute": {
                    "slug": "username",
                    "label": "Username",
                    "attribute_type": "string",
                    "attribute_sub_type": None,
                },
            }
        ],
        "relationship_schemas": [],
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
            return_value=Response(
                200, json={"entity_schemas": [], "relationship_schemas": []}
            )
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


class TestSyncGetDecision:
    """Tests for the synchronous get_decision method."""

    @respx.mock
    def test_get_decision_success(self, client, sample_decision):
        """Test successful retrieval of a single decision."""
        route = respx.get("https://api.example.com/api/v1/decisions/abc-123/").mock(
            return_value=Response(200, json=sample_decision)
        )

        with client:
            decision = client.get_decision("abc-123")

        assert route.called
        assert isinstance(decision, DecisionSchema)
        assert decision.uuid == "abc-123"
        assert decision.user == "reviewer@example.com"
        assert decision.entity.entity_type == "user"
        assert decision.notes == "Looks fine"
        assert decision.is_training is False

    @respx.mock
    def test_get_decision_not_found(self, client):
        """Test handling of 404 when decision does not exist."""
        respx.get("https://api.example.com/api/v1/decisions/nonexistent/").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        with client:
            with pytest.raises(Exception) as exc_info:
                client.get_decision("nonexistent")

            assert "404" in str(exc_info.value)

    @respx.mock
    def test_get_decision_with_auth_header(self, client, sample_decision):
        """Test that authorization header is sent correctly."""
        route = respx.get("https://api.example.com/api/v1/decisions/abc-123/").mock(
            return_value=Response(200, json=sample_decision)
        )

        with client:
            client.get_decision("abc-123")

        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer test-token"


class TestSyncListDecisions:
    """Tests for the synchronous list_decisions method."""

    @respx.mock
    def test_list_decisions_success(self, client, sample_decision):
        """Test successful retrieval of paginated decisions."""
        paged = {"items": [sample_decision], "count": 1}
        route = respx.get("https://api.example.com/api/v1/decisions/").mock(
            return_value=Response(200, json=paged)
        )

        with client:
            result = client.list_decisions()

        assert route.called
        assert isinstance(result, PagedDecisionSchema)
        assert result.count == 1
        assert len(result.items) == 1
        assert result.items[0].uuid == "abc-123"

    @respx.mock
    def test_list_decisions_with_pagination(self, client, sample_decision):
        """Test that limit and offset are sent as query parameters."""
        paged = {"items": [sample_decision], "count": 50}
        route = respx.get("https://api.example.com/api/v1/decisions/").mock(
            return_value=Response(200, json=paged)
        )

        with client:
            client.list_decisions(limit=10, offset=20)

        request = route.calls.last.request
        assert "limit=10" in str(request.url)
        assert "offset=20" in str(request.url)

    @respx.mock
    def test_list_decisions_with_filters(self, client, sample_decision):
        """Test that filters are sent as query parameters."""
        from cinder.generated.models import DecisionFilter

        paged = {"items": [sample_decision], "count": 1}
        route = respx.get("https://api.example.com/api/v1/decisions/").mock(
            return_value=Response(200, json=paged)
        )

        filters = DecisionFilter(queue="default", entity_id="u1")
        with client:
            client.list_decisions(filters=filters)

        request = route.calls.last.request
        assert "queue=default" in str(request.url)
        assert "entity_id=u1" in str(request.url)

    @respx.mock
    def test_list_decisions_empty(self, client):
        """Test retrieval of empty decision list."""
        paged = {"items": [], "count": 0}
        route = respx.get("https://api.example.com/api/v1/decisions/").mock(
            return_value=Response(200, json=paged)
        )

        with client:
            result = client.list_decisions()

        assert route.called
        assert isinstance(result, PagedDecisionSchema)
        assert result.count == 0
        assert len(result.items) == 0


class TestSyncGetDecisionReports:
    """Tests for the synchronous get_decision_reports method."""

    @respx.mock
    def test_get_decision_reports_success(self, client, sample_report):
        """Test successful retrieval of reports for a decision."""
        route = respx.get(
            "https://api.example.com/api/v2/decisions/abc-123/reports/"
        ).mock(return_value=Response(200, json=[sample_report]))

        with client:
            reports = client.get_decision_reports("abc-123")

        assert route.called
        assert len(reports) == 1
        assert isinstance(reports[0], Report)
        assert reports[0].reasoning == "Spam content"
        assert reports[0].entity.entity_schema == "message"
        assert reports[0].reporter.entity_schema == "user"
        assert reports[0].attribute_slugs == ["body"]

    @respx.mock
    def test_get_decision_reports_empty(self, client):
        """Test retrieval when decision has no reports."""
        route = respx.get(
            "https://api.example.com/api/v2/decisions/abc-123/reports/"
        ).mock(return_value=Response(200, json=[]))

        with client:
            reports = client.get_decision_reports("abc-123")

        assert route.called
        assert reports == []

    @respx.mock
    def test_get_decision_reports_not_found(self, client):
        """Test handling of 404 when decision does not exist."""
        respx.get("https://api.example.com/api/v2/decisions/nonexistent/reports/").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        with client:
            with pytest.raises(Exception) as exc_info:
                client.get_decision_reports("nonexistent")

            assert "404" in str(exc_info.value)

    @respx.mock
    def test_get_decision_reports_with_auth_header(self, client, sample_report):
        """Test that authorization header is sent correctly."""
        route = respx.get(
            "https://api.example.com/api/v2/decisions/abc-123/reports/"
        ).mock(return_value=Response(200, json=[sample_report]))

        with client:
            client.get_decision_reports("abc-123")

        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer test-token"


class TestSyncListReports:
    """Tests for the synchronous list_reports method."""

    @respx.mock
    def test_list_reports_success(self, client, sample_report):
        """Test successful retrieval of paginated reports."""
        paged = {"items": [sample_report], "count": 1}
        route = respx.get("https://api.example.com/api/v1/report/").mock(
            return_value=Response(200, json=paged)
        )

        with client:
            result = client.list_reports()

        assert route.called
        assert isinstance(result, PagedReport)
        assert result.count == 1
        assert len(result.items) == 1
        assert isinstance(result.items[0], Report)
        assert result.items[0].reasoning == "Spam content"

    @respx.mock
    def test_list_reports_with_pagination(self, client, sample_report):
        """Test that limit and offset are sent as query parameters."""
        paged = {"items": [sample_report], "count": 50}
        route = respx.get("https://api.example.com/api/v1/report/").mock(
            return_value=Response(200, json=paged)
        )

        with client:
            client.list_reports(limit=10, offset=20)

        request = route.calls.last.request
        assert "limit=10" in str(request.url)
        assert "offset=20" in str(request.url)

    @respx.mock
    def test_list_reports_empty(self, client):
        """Test retrieval of empty report list."""
        paged = {"items": [], "count": 0}
        route = respx.get("https://api.example.com/api/v1/report/").mock(
            return_value=Response(200, json=paged)
        )

        with client:
            result = client.list_reports()

        assert route.called
        assert isinstance(result, PagedReport)
        assert result.count == 0
        assert len(result.items) == 0

    @respx.mock
    def test_list_reports_with_auth_header(self, client, sample_report):
        """Test that authorization header is sent correctly."""
        paged = {"items": [sample_report], "count": 1}
        route = respx.get("https://api.example.com/api/v1/report/").mock(
            return_value=Response(200, json=paged)
        )

        with client:
            client.list_reports()

        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer test-token"
