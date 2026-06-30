import os


class DevEnvSecretResolver:
    """Reads secrets from DAGSTER__<GROUP>__<KEY> environment variables.

    Suitable for local dev and CI. Replace with your production secret
    backend (e.g. AWS Secrets Manager, GCP Secret Manager) for live runs.
    """

    def resolve_as_str(self, ref) -> str:
        env = f"DAGSTER__{ref.group_name.upper()}__{ref.key.upper()}"
        val = os.getenv(env)
        if val is None:
            raise RuntimeError(
                f"Missing required env var: {env}\n"
                f"Set it before running: export {env}=<value>"
            )
        return val
