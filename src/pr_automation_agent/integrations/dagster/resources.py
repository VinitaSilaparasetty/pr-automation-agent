"""Dagster resource wrapping DevEnvSecretResolver."""

from dagster import resource
from pr_automation_agent.resolvers import DevEnvSecretResolver


@resource
def dev_env_secret_resolver_resource():
    """Dagster resource that resolves secrets from ``PR_AGENT__*`` environment variables.

    Register under the key ``secret_resolver`` in your ``Definitions``::

        from pr_automation_agent.integrations.dagster import dev_env_secret_resolver_resource

        defs = Definitions(
            assets=assets,
            resources={"secret_resolver": dev_env_secret_resolver_resource},
        )
    """
    return DevEnvSecretResolver()
