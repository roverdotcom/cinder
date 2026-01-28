"""Base client with shared functionality."""
from typing import Any, Dict, Optional


class BaseCinderClient:
    """Base class with shared functionality for Cinder API clients."""

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 30.0,
        **kwargs: Any,
    ):
        """Initialize the base client.

        Args:
            base_url: Base URL for the Cinder API
            token: API authentication token
            timeout: Request timeout in seconds
            **kwargs: Additional arguments passed to httpx client
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

        # Prepare headers
        self.headers = kwargs.pop("headers", {})
        self.headers.setdefault("Authorization", f"Bearer {token}")
        self.headers.setdefault("Content-Type", "application/json")

        self.extra_kwargs = kwargs

    def _build_params(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """Build query parameters for list endpoints.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            **extra_params: Additional parameters

        Returns:
            Dictionary of query parameters
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params.update(extra_params)
        return params
