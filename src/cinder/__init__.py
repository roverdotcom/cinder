"""Cinder API client library."""
from .client import CinderClient, get_client
from .sync_client import SyncCinderClient, get_sync_client

# Export commonly used models for convenience
from .generated.models import (
    Appeal,
    AppealFilterSchema,
    CreateAppealSchema,
    CreateDecisionSchema,
    CreateEntitiesAndRelationshipsResponseSchema,
    CreateEntitiesAndRelationshipsSchema,
    CreateReportSchema,
    CustomerEvent,
    CustomerEventEntitySubgraph,
    DecisionFilter,
    DecisionSchema,
    EntityApiSchema,
    EventEntity,
    EventRelationship,
    PagedAppeal,
    PagedDecisionSchema,
    PagedReport,
    RelationshipApiSchema,
    Report,
    ReportSchema,
    StatusOkResponse,
    WorkflowResult,
)

__all__ = [
    # Async Client
    "CinderClient",
    "get_client",
    # Sync Client
    "SyncCinderClient",
    "get_sync_client",
    # Common models
    "Appeal",
    "AppealFilterSchema",
    "CreateAppealSchema",
    "CreateDecisionSchema",
    "CreateEntitiesAndRelationshipsResponseSchema",
    "CreateEntitiesAndRelationshipsSchema",
    "CreateReportSchema",
    "CustomerEvent",
    "CustomerEventEntitySubgraph",
    "DecisionFilter",
    "DecisionSchema",
    "EntityApiSchema",
    "EventEntity",
    "EventRelationship",
    "PagedAppeal",
    "PagedDecisionSchema",
    "PagedReport",
    "RelationshipApiSchema",
    "Report",
    "ReportSchema",
    "StatusOkResponse",
    "WorkflowResult",
]

# Optional Django helpers
try:
    from .django_helpers import (
        DjangoSyncCinderClient,
        get_sync_client_from_settings,
    )

    __all__.extend(["DjangoSyncCinderClient", "get_sync_client_from_settings"])
except ImportError:
    # Django not installed, helpers not available
    pass
