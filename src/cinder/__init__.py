"""Cinder API client library."""

from .client import CinderClient
from .client import get_client

# Export commonly used models for convenience
from .generated.models import Appeal
from .generated.models import AppealFilterSchema
from .generated.models import CreateAppealSchema
from .generated.models import CreateDecisionSchema
from .generated.models import CreateEntitiesAndRelationshipsResponseSchema
from .generated.models import CreateEntitiesAndRelationshipsSchema
from .generated.models import CreateReportSchema
from .generated.models import CustomerEvent
from .generated.models import CustomerEventEntitySubgraph
from .generated.models import DecisionFilter
from .generated.models import DecisionSchema
from .generated.models import EntityApiSchema
from .generated.models import EventEntity
from .generated.models import EventRelationship
from .generated.models import PagedAppeal
from .generated.models import PagedDecisionSchema
from .generated.models import PagedReport
from .generated.models import RelationshipApiSchema
from .generated.models import Report
from .generated.models import ReportSchema
from .generated.models import StatusOkResponse
from .generated.models import WorkflowResult
from .sync_client import SyncCinderClient
from .sync_client import get_sync_client


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
    from .django_helpers import DjangoSyncCinderClient
    from .django_helpers import get_sync_client_from_settings

    __all__.extend(["DjangoSyncCinderClient", "get_sync_client_from_settings"])
except ImportError:
    # Django not installed, helpers not available
    pass
