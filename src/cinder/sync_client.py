"""Synchronous Cinder API client wrapper."""
import os
from typing import Any, Optional

import httpx

from .base_client import BaseCinderClient
from .generated.models import (
    Appeal,
    CreateDecisionSchema,
    CreateReportSchema,
    DecisionFilter,
    DecisionSchema,
    PagedAppeal,
    PagedDecisionSchema,
    PagedReport,
    Report,
    SchemaResponse,
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
