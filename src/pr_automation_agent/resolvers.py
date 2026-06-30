"""Secret resolution — env-based dev resolver and abstract interface."""

import abc
import os
from typing import NamedTuple

from dagster import resource


class SecretReference(NamedTuple):
    """Identifies a secret by logical group and key."""
    group_name: str
    key: str


class AbstractSecretResolver(abc.ABC):
    """Implement this to connect to your production secret backend.

    Examples: AWS SSM Parameter Store, GCP Secret Manager, Azure Key Vault,
    HashiCorp Vault. Register the concrete class as the ``secret_resolver``
    Dagster resource in your ``Definitions``.
    """

    @abc.abstractmethod
    def resolve_as_str(self, ref: SecretReference) -> str:
        """Return the secret value as a string, or raise RuntimeError if missing."""
        ...


class DevEnvSecretResolver(AbstractSecretResolver):
    """Reads secrets from ``DAGSTER__<GROUP>__<KEY>`` environment variables.

    Suitable for local development and CI. Replace with a production resolver
    (e.g. ``AwsSsmSecretResolver``) before deploying to a live environment.
    """

    def resolve_as_str(self, ref: SecretReference) -> str:
        env = f"DAGSTER__{ref.group_name.upper()}__{ref.key.upper()}"
        val = os.getenv(env)
        if val is None:
            raise RuntimeError(
                f"Missing secret: {env}\n"
                f"Set it before running:  export {env}=<value>\n"
                "In production replace DevEnvSecretResolver with your secret backend."
            )
        return val


@resource
def dev_env_secret_resolver_resource():
    """Dagster resource that resolves secrets from environment variables.

    Register this in your ``Definitions`` under the key ``secret_resolver``::

        from pr_automation_agent import dev_env_secret_resolver_resource

        defs = Definitions(
            assets=assets,
            resources={"secret_resolver": dev_env_secret_resolver_resource},
        )
    """
    return DevEnvSecretResolver()
