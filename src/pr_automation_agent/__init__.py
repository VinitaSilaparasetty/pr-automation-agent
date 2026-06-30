"""pr-automation-agent — framework-agnostic core.

For Dagster-specific helpers (BaseRestAsset, dev_env_secret_resolver_resource, etc.)
see ``pr_automation_agent.integrations.dagster``.
"""

from .resolvers import (
    AbstractSecretResolver,
    DevEnvSecretResolver,
    SecretReference,
)
from .audit import log_ai_contribution
from .base import (
    BaseRestFetcher,
    BaseGraphQLFetcher,
    PaginatedGraphQLFetcher,
    BaseDbReplicator,
)

__all__ = [
    # Secrets
    "AbstractSecretResolver",
    "DevEnvSecretResolver",
    "SecretReference",
    # Audit
    "log_ai_contribution",
    # Base fetcher/replicator classes
    "BaseRestFetcher",
    "BaseGraphQLFetcher",
    "PaginatedGraphQLFetcher",
    "BaseDbReplicator",
]
