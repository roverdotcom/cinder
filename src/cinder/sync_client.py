"""Synchronous Cinder API client wrapper."""
import os
from typing import Any, Optional

import httpx

from .base_client import BaseCinderClient
from .generated.models import (
    Appeal,
    CreateDecisionSchema,
    CreateEntitiesAndRelationshipsResponseSchema,
    CreateEntitiesAndRelationshipsSchema,
    CreateReportSchema,
    CustomerEvent,
    DecisionFilter,
    DecisionSchema,
    EntityApiSchema,
    PagedAppeal,
    PagedDecisionSchema,
    PagedReport,
    RelationshipApiSchema,
    Report,
    SchemaResponse,
    StatusOkResponse,
    WorkflowResult,
)


class SyncCinderClient(BaseCinderClient):
    """Synchronous HTTP client for Cinder API.

    This is a synchronous version of CinderClient that uses httpx.Client
    instead of httpx.AsyncClient. Useful for Django synchronous views,
    management commands, and other non-async contexts.

    Example:
        ```python
        with SyncCinderClient(base_url="https://api.example.com", token="your-token") as client:
            # Create a report
            report = client.create_report(
                CreateReportSchema(
                    entity={"type": "user", "id": "123"},
                    # ... other fields
                )
            )

            # Get decisions
            decisions = client.list_decisions(limit=10)
        ```
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 30.0,
        **kwargs: Any,
    ):
        """Initialize the Cinder API client.

        Args:
            base_url: Base URL for the Cinder API (e.g., "https://api.example.com")
            token: API authentication token
            timeout: Request timeout in seconds (default: 30.0)
            **kwargs: Additional arguments passed to httpx.Client
        """
        super().__init__(base_url, token, timeout, **kwargs)

        # Create sync HTTP client
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            **self.extra_kwargs,
        )

    def __enter__(self) -> "SyncCinderClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    # -------------------------------------------------------------------------
    # Reports
    # -------------------------------------------------------------------------

    def create_report(self, report: CreateReportSchema) -> Report:
        """Create a new report.

        Args:
            report: Report data to create

        Returns:
            Created report

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = self.client.post(
            "/api/v1/create_report/",
            json=report.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return Report.model_validate(response.json())

    def list_reports(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters: Any,
    ) -> PagedReport:
        """List reports with optional filtering.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            **filters: Additional filter parameters

        Returns:
            Paginated list of reports
        """
        params = self._build_params(limit, offset, **filters)
        response = self.client.get("/api/v1/report/", params=params)
        response.raise_for_status()
        return PagedReport.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Decisions
    # -------------------------------------------------------------------------

    def create_decision(self, decision: CreateDecisionSchema) -> DecisionSchema:
        """Create a new decision.

        Args:
            decision: Decision data to create

        Returns:
            Created decision

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = self.client.post(
            "/api/v1/create_decision/",
            json=decision.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return DecisionSchema.model_validate(response.json())

    def get_decision(self, decision_id: str) -> DecisionSchema:
        """Get a decision by ID.

        Args:
            decision_id: The decision ID

        Returns:
            Decision details

        Raises:
            httpx.HTTPStatusError: If the request fails or decision not found
        """
        response = self.client.get(f"/api/v1/decisions/{decision_id}/")
        response.raise_for_status()
        return DecisionSchema.model_validate(response.json())

    def list_decisions(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filters: Optional[DecisionFilter] = None,
        **extra_params: Any,
    ) -> PagedDecisionSchema:
        """List decisions with optional filtering.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            filters: Structured filters
            **extra_params: Additional query parameters

        Returns:
            Paginated list of decisions
        """
        params = self._build_params(limit, offset, **extra_params)
        if filters is not None:
            params.update(filters.model_dump(mode="json", exclude_none=True))

        response = self.client.get("/api/v1/decisions/", params=params)
        response.raise_for_status()
        return PagedDecisionSchema.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Appeals
    # -------------------------------------------------------------------------

    def get_appeal(self, appeal_id: str) -> Appeal:
        """Get an appeal by ID.

        Args:
            appeal_id: The appeal ID

        Returns:
            Appeal details

        Raises:
            httpx.HTTPStatusError: If the request fails or appeal not found
        """
        response = self.client.get(f"/api/v1/appeal/{appeal_id}/")
        response.raise_for_status()
        return Appeal.model_validate(response.json())

    def list_appeals(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters: Any,
    ) -> PagedAppeal:
        """List appeals with optional filtering.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            **filters: Additional filter parameters

        Returns:
            Paginated list of appeals
        """
        params = self._build_params(limit, offset, **filters)
        response = self.client.get("/api/v1/appeal/", params=params)
        response.raise_for_status()
        return PagedAppeal.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Graph Schema
    # -------------------------------------------------------------------------

    def get_graph_schema(self) -> SchemaResponse:
        """Get the complete graph schema.

        Returns the entity schemas and relationship schemas that define
        the structure of the Cinder graph.

        Returns:
            Complete graph schema including entity and relationship schemas

        Raises:
            httpx.HTTPStatusError: If the request fails

        Example:
            ```python
            with client:
                schema = client.get_graph_schema()
                print(f"Found {len(schema.entity_schemas)} entity schemas")
                print(f"Found {len(schema.relationship_schemas)} relationship schemas")
            ```
        """
        response = self.client.get("/api/v1/graph/schema/")
        response.raise_for_status()
        return SchemaResponse.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Graph (Entities & Relationships)
    # -------------------------------------------------------------------------

    def upsert(
        self,
        entities: Optional[list[EntityApiSchema]] = None,
        relationships: Optional[list[RelationshipApiSchema]] = None,
    ) -> CreateEntitiesAndRelationshipsResponseSchema:
        """Upsert entities and relationships to the Cinder graph.

        This endpoint creates or updates entities and relationships that adhere to
        your Cinder schema. Entities are identified by their entity_type and id attribute.
        If an entity with the same type and id already exists, it will be updated.

        Args:
            entities: List of entities to upsert, each containing entity_type, attributes,
                     and optional classifier_scores
            relationships: List of relationships to create between entities

        Returns:
            Response containing the created/updated entities and relationships

        Raises:
            httpx.HTTPStatusError: If the request fails (403 Forbidden, 422 Validation Error)

        Example:
            ```python
            with client:
                result = client.upsert(
                    entities=[
                        EntityApiSchema(
                            entity_type="user",
                            attributes={"id": "user123", "name": "John Doe"}
                        ),
                        EntityApiSchema(
                            entity_type="post",
                            attributes={"id": "post456", "content": "Hello world"}
                        )
                    ],
                    relationships=[
                        RelationshipApiSchema(
                            source_type="user",
                            source_id="user123",
                            target_type="post",
                            target_id="post456",
                            relationship_type="author_of"
                        )
                    ]
                )
            ```
        """
        payload = CreateEntitiesAndRelationshipsSchema(
            entities=entities,
            relationships=relationships,
        )
        response = self.client.post(
            "/api/v1/graph/",
            json=payload.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return CreateEntitiesAndRelationshipsResponseSchema.model_validate(
            response.json()
        )

    # -------------------------------------------------------------------------
    # Events
    # -------------------------------------------------------------------------

    def send_event(self, event: CustomerEvent) -> StatusOkResponse:
        """Send an event to Cinder for asynchronous processing.

        This endpoint enqueues the event to be processed by workflows. Returns immediately
        without waiting for workflow execution to complete.

        Args:
            event: Customer event data containing event_name, entity, and optional subgraph

        Returns:
            StatusOkResponse indicating the event was enqueued (200) or no enabled
            workflow exists to process it (202)

        Raises:
            httpx.HTTPStatusError: If the request fails

        Example:
            ```python
            with client:
                event = CustomerEvent(
                    event_name="user.signup",
                    entity=EventEntity(
                        entity_schema="User",
                        attributes={"id": "123", "email": "user@example.com"}
                    )
                )
                result = client.send_event(event)
            ```
        """
        response = self.client.post(
            "/api/v2/workflows/event/",
            json=event.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return StatusOkResponse.model_validate(response.json())

    def send_event_sync(self, event: CustomerEvent) -> WorkflowResult | StatusOkResponse:
        """Send an event to Cinder for synchronous processing.

        This endpoint processes the event immediately and waits for workflow execution
        to complete before returning the result. Use this when you need immediate
        feedback, but be mindful of latency and fault tolerance considerations.

        Args:
            event: Customer event data containing event_name, entity, and optional subgraph

        Returns:
            WorkflowResult with workflow execution details (200) or StatusOkResponse
            if no enabled workflow exists (202)

        Raises:
            httpx.HTTPStatusError: If the request fails, event is invalid (422),
                                   or workflow execution exceeds 60s timeout (504)

        Example:
            ```python
            with client:
                event = CustomerEvent(
                    event_name="content.created",
                    entity=EventEntity(
                        entity_schema="Post",
                        attributes={"id": "456", "content": "Hello world"}
                    )
                )
                result = client.send_event_sync(event)
                if isinstance(result, WorkflowResult):
                    print(f"Workflow executed: {result.path}")
            ```
        """
        response = self.client.post(
            "/api/v2/workflows/event/sync/",
            json=event.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()

        # Check response status to determine which model to use
        if response.status_code == 202:
            return StatusOkResponse.model_validate(response.json())
        return WorkflowResult.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Generic request methods
    # -------------------------------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a generic HTTP request.

        Useful for endpoints not yet wrapped by convenience methods.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (will be appended to base_url)
            **kwargs: Additional arguments passed to httpx

        Returns:
            HTTP response

        Example:
            ```python
            response = client.request("GET", "/api/v1/custom-endpoint/")
            data = response.json()
            ```
        """
        response = self.client.request(method, path, **kwargs)
        response.raise_for_status()
        return response


def get_sync_client(
    token: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs: Any,
) -> SyncCinderClient:
    """Create an authenticated synchronous Cinder API client.

    This is a convenience function that reads configuration from environment
    variables if not provided explicitly.

    Args:
        token: API token. If not provided, reads from CINDER_API_TOKEN env var.
        base_url: Base URL for the API. If not provided, reads from CINDER_API_BASE_URL env var.
        **kwargs: Additional arguments passed to SyncCinderClient constructor.

    Returns:
        SyncCinderClient instance configured with authentication.

    Raises:
        ValueError: If token is not provided and CINDER_API_TOKEN env var is not set.
        ValueError: If base_url is not provided and CINDER_API_BASE_URL env var is not set.

    Example:
        ```python
        # Using environment variables
        client = get_sync_client()

        # Or explicitly
        client = get_sync_client(
            token="your-token",
            base_url="https://api.example.com"
        )

        with client:
            decisions = client.list_decisions()
        ```
    """
    if token is None:
        token = os.environ.get("CINDER_API_TOKEN")
        if not token:
            raise ValueError(
                "API token must be provided via 'token' parameter or CINDER_API_TOKEN environment variable"
            )

    if base_url is None:
        base_url = os.environ.get("CINDER_API_BASE_URL")
        if not base_url:
            raise ValueError(
                "Base URL must be provided via 'base_url' parameter or CINDER_API_BASE_URL environment variable"
            )

    return SyncCinderClient(
        base_url=base_url,
        token=token,
        **kwargs,
    )
