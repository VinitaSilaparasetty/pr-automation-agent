"""Secret resolution — framework-agnostic resolver interface and env-var implementation."""

import abc
import os
from typing import NamedTuple


class SecretReference(NamedTuple):
    """Identifies a secret by logical group and key."""
    group_name: str
    key: str


class AbstractSecretResolver(abc.ABC):
    """Implement this to connect to your production secret backend.

    Examples: AWS SSM Parameter Store, GCP Secret Manager, Azure Key Vault,
    HashiCorp Vault. Pass an instance to ``BaseDbReplicator.__init__`` or
    register it as a resource in your pipeline framework.
    """

    @abc.abstractmethod
    def resolve_as_str(self, ref: SecretReference) -> str:
        """Return the secret value as a string, or raise RuntimeError if missing."""
        ...


class DevEnvSecretResolver(AbstractSecretResolver):
    """Reads secrets from ``PR_AGENT__<GROUP>__<KEY>`` environment variables.

    Suitable for local development and CI. Replace with a production resolver
    (e.g. an AWS SSM or GCP Secret Manager implementation) before deploying live.

    Example::

        export PR_AGENT__POSTGRES__URI="postgresql://user:pw@host/db"
        export PR_AGENT__POSTGRES__SINCE="2024-01-01"
    """

    def resolve_as_str(self, ref: SecretReference) -> str:
        env = f"PR_AGENT__{ref.group_name.upper()}__{ref.key.upper()}"
        val = os.getenv(env)
        if val is None:
            raise RuntimeError(
                f"Missing secret: {env}\n"
                f"Set it before running:  export {env}=<value>\n"
                "In production replace DevEnvSecretResolver with your secret backend."
            )
        return val
