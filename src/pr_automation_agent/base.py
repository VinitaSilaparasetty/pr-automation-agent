"""Framework-agnostic base classes for the three core ingest patterns.

These classes have no dependency on Dagster, Prefect, Airflow, or any other
pipeline framework. Subclass one and implement the single abstract method;
call ``.run()`` from wherever your pipeline expects it.

For Dagster-specific wrappers (``@asset``, ``AssetExecutionContext``) see
``pr_automation_agent.integrations.dagster``.
"""

import abc
import json
import pathlib
import datetime as dt
from typing import Any

from .resolvers import AbstractSecretResolver, DevEnvSecretResolver, SecretReference


class BaseRestFetcher(abc.ABC):
    """Base for REST ingest fetchers.

    Usage::

        class StripeInvoices(BaseRestFetcher):
            provider = "stripe"
            entity = "invoices"

            def fetch_all(self) -> list[dict]:
                import requests
                r = requests.get(
                    "https://api.stripe.com/v1/invoices",
                    headers={"Authorization": f"Bearer {os.environ['STRIPE_KEY']}"},
                    timeout=60,
                )
                r.raise_for_status()
                return r.json()["data"]

        path, rows = StripeInvoices().run()
        print(f"Wrote {rows} rows to {path}")
    """

    provider: str
    entity: str
    output_root: pathlib.Path = pathlib.Path("tmp")

    @abc.abstractmethod
    def fetch_all(self) -> list[dict[str, Any]]:
        """Fetch all records from the source. Handle pagination here."""
        ...

    def output_path(self) -> pathlib.Path:
        out = self.output_root / self.provider / self.entity
        out.mkdir(parents=True, exist_ok=True)
        return out / f"{dt.date.today().isoformat()}.json"

    def run(self) -> tuple[str, int]:
        """Fetch, write to disk, return ``(path, row_count)``."""
        items = self.fetch_all()
        fp = self.output_path()
        fp.write_text(json.dumps(items, default=str), encoding="utf-8")
        return str(fp), len(items)


class BaseGraphQLFetcher(abc.ABC):
    """Base for single-request GraphQL fetchers.

    For cursor-based pagination use ``PaginatedGraphQLFetcher`` instead.

    Usage::

        class CountriesData(BaseGraphQLFetcher):
            provider = "countries"
            entity = "countries"
            url = "https://countries.trevorblades.com/"
            query = "{ countries { code name } }"

            def extract_records(self, data: dict) -> list[dict]:
                return data["countries"]

        path, rows = CountriesData().run()
    """

    provider: str
    entity: str
    url: str
    query: str
    output_root: pathlib.Path = pathlib.Path("tmp")

    @abc.abstractmethod
    def extract_records(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract the records list from the GraphQL ``data`` response object."""
        ...

    def fetch_all(self) -> list[dict[str, Any]]:
        import requests  # noqa: PLC0415
        r = requests.post(self.url, json={"query": self.query}, timeout=60)
        r.raise_for_status()
        return self.extract_records(r.json().get("data", {}))

    def output_path(self) -> pathlib.Path:
        out = self.output_root / self.provider / self.entity
        out.mkdir(parents=True, exist_ok=True)
        return out / f"{dt.date.today().isoformat()}.json"

    def run(self) -> tuple[str, int]:
        """Fetch, write to disk, return ``(path, row_count)``."""
        items = self.fetch_all()
        fp = self.output_path()
        fp.write_text(json.dumps(items, default=str), encoding="utf-8")
        return str(fp), len(items)


class PaginatedGraphQLFetcher(BaseGraphQLFetcher):
    """Base for cursor-paginated GraphQL fetchers.

    Implement ``build_query(cursor)`` and ``extract_page(data)``
    instead of ``query`` and ``extract_records``.

    Usage::

        class GithubIssues(PaginatedGraphQLFetcher):
            provider = "github"
            entity = "issues"
            url = "https://api.github.com/graphql"

            def build_query(self, cursor: str | None) -> str:
                after = f', after: "{cursor}"' if cursor else ""
                return f'{{ repository(owner:"octocat", name:"hello-world") {{ issues(first:100{after}) {{ nodes {{ number title }} pageInfo {{ hasNextPage endCursor }} }} }} }}'

            def extract_page(self, data: dict) -> tuple[list[dict], str | None]:
                conn = data["repository"]["issues"]
                cursor = conn["pageInfo"]["endCursor"] if conn["pageInfo"]["hasNextPage"] else None
                return conn["nodes"], cursor
    """

    query: str = ""  # unused in paginated mode

    @abc.abstractmethod
    def build_query(self, cursor: str | None) -> str: ...

    @abc.abstractmethod
    def extract_page(self, data: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]: ...

    def extract_records(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError("Use build_query / extract_page for paginated fetchers.")

    def fetch_all(self) -> list[dict[str, Any]]:
        import requests  # noqa: PLC0415
        all_records: list[dict] = []
        cursor: str | None = None
        while True:
            r = requests.post(
                self.url, json={"query": self.build_query(cursor)}, timeout=60
            )
            r.raise_for_status()
            records, cursor = self.extract_page(r.json().get("data", {}))
            all_records.extend(records)
            if cursor is None:
                break
        return all_records


class BaseDbReplicator(abc.ABC):
    """Base for incremental DB replication fetchers.

    Pass a ``secret_resolver`` at construction, or set
    ``PR_AGENT__<ENGINE>__URI`` and ``PR_AGENT__<ENGINE>__SINCE`` env vars
    to use the default ``DevEnvSecretResolver``.

    Usage::

        class PostgresOrders(BaseDbReplicator):
            engine_name = "postgres"
            table = "orders"

            def get_query(self, since: str) -> str:
                return "SELECT * FROM orders WHERE updated_at >= :since"

        path, rows = PostgresOrders().run()           # reads PR_AGENT__POSTGRES__* envs
        # or:
        path, rows = PostgresOrders(my_resolver).run()
    """

    engine_name: str
    table: str
    output_root: pathlib.Path = pathlib.Path("tmp")

    def __init__(self, secret_resolver: AbstractSecretResolver | None = None) -> None:
        self._resolver = secret_resolver or DevEnvSecretResolver()

    @abc.abstractmethod
    def get_query(self, since: str) -> str:
        """Return the SQL with a ``:since`` bind parameter for the watermark."""
        ...

    def run(self) -> tuple[str, int]:
        """Replicate, write Parquet to disk, return ``(path, row_count)``."""
        return self._run_with_resolver(self._resolver)

    def _run_with_resolver(self, resolver: AbstractSecretResolver) -> tuple[str, int]:
        try:
            from sqlalchemy import create_engine, text
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "DB replication requires sqlalchemy and pandas.\n"
                'Install with:  pip install "pr-automation-agent[dagster]"'
            ) from exc

        uri = resolver.resolve_as_str(SecretReference(self.engine_name.upper(), "URI"))
        since = resolver.resolve_as_str(SecretReference(self.engine_name.upper(), "SINCE"))

        eng = create_engine(uri)
        df = pd.read_sql(text(self.get_query(since)), eng, params={"since": since})

        out = self.output_root / self.engine_name / self.table
        out.mkdir(parents=True, exist_ok=True)
        fp = out / f"{dt.date.today().isoformat()}.parquet"
        df.to_parquet(fp, index=False)
        return str(fp), len(df)
