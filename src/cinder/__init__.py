"""Cinder API client library."""
from .client import CinderClient, get_client

# Export commonly used models for convenience
from .generated.models import (
    Appeal,
    AppealFilterSchema,
    CreateAppealSchema,
    CreateDecisionSchema,
    CreateReportSchema,
    DecisionFilter,
    DecisionSchema,
    PagedAppeal,
    PagedDecisionSchema,
    PagedReport,
    Report,
    ReportSchema,
)

__all__ = [
    # Client
    "CinderClient",
    "get_client",
    # Common models
    "Appeal",
    "AppealFilterSchema",
    "CreateAppealSchema",
    "CreateDecisionSchema",
    "CreateReportSchema",
    "DecisionFilter",
    "DecisionSchema",
    "PagedAppeal",
    "PagedDecisionSchema",
    "PagedReport",
    "Report",
    "ReportSchema",
]
