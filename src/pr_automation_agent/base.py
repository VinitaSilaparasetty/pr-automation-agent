"""Abstract base classes for the three core ingest patterns.

Subclass one of these and implement the single abstract method.
The base handles file I/O, metadata, and output path conventions.
"""

import abc
import json
import pathlib
import datetime as dt
from typing import Any

from dagster import AssetExecutionContext, MetadataValue

from .resolvers import AbstractSecretResolver, SecretReference


class BaseRestAsset(abc.ABC):
    """Base for REST crawl assets.

    Usage::

        class MyApiInvoices(BaseRestAsset):
            provider = "myapi"
            entity = "invoices"

            def fetch_all(self) -> list[dict]:
                import requests
                r = requests.get("https://api.myservice.com/invoices", timeout=60)
                r.raise_for_status()
                return r.json()

        @asset(group_name="rest_crawl")
        def fetch_myapi_invoices(context: AssetExecutionContext) -> str:
            return MyApiInvoices().materialize(context)
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

    def materialize(self, context: AssetExecutionContext) -> str:
        items = self.fetch_all()
        fp = self.output_path()
        fp.write_text(json.dumps(items, default=str), encoding="utf-8")
        context.add_output_metadata({
            "rows": MetadataValue.int(len(items)),
            "path": MetadataValue.path(str(fp)),
        })
        return str(fp)


class BaseGraphQLAsset(abc.ABC):
    """Base for single-request GraphQL crawl assets.

    For cursor-based pagination use ``PaginatedGraphQLAsset`` instead.

    Usage::

        class GithubRepos(BaseGraphQLAsset):
            provider = "github"
            entity = "repos"
            url = "https://api.github.com/graphql"
            query = "{ viewer { repositories(first: 100) { nodes { name } } } }"

            def extract_records(self, data: dict) -> list[dict]:
                return data["viewer"]["repositories"]["nodes"]

        @asset(group_name="graphql_crawl")
        def fetch_github_repos(context: AssetExecutionContext) -> str:
            return GithubRepos().materialize(context)
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
        import requests  # noqa: PLC0415 — optional at class definition time
        r = requests.post(self.url, json={"query": self.query}, timeout=60)
        r.raise_for_status()
        return self.extract_records(r.json().get("data", {}))

    def output_path(self) -> pathlib.Path:
        out = self.output_root / self.provider / self.entity
        out.mkdir(parents=True, exist_ok=True)
        return out / f"{dt.date.today().isoformat()}.json"

    def materialize(self, context: AssetExecutionContext) -> str:
        items = self.fetch_all()
        fp = self.output_path()
        fp.write_text(json.dumps(items, default=str), encoding="utf-8")
        context.add_output_metadata({
            "rows": MetadataValue.int(len(items)),
            "path": MetadataValue.path(str(fp)),
        })
        return str(fp)


class PaginatedGraphQLAsset(BaseGraphQLAsset):
    """Base for cursor-paginated GraphQL assets.

    Implement ``build_query(cursor)`` and ``extract_page(data)``
    instead of ``query`` and ``extract_records``.

    Usage::

        class GithubIssues(PaginatedGraphQLAsset):
            provider = "github"
            entity = "issues"
            url = "https://api.github.com/graphql"

            def build_query(self, cursor: str | None) -> str:
                after = f', after: "{cursor}"' if cursor else ""
                return f'''
                  {{ repository(owner:"octocat", name:"hello-world") {{
                    issues(first: 100{after}) {{
                      nodes {{ number title }}
                      pageInfo {{ hasNextPage endCursor }}
                    }}
                  }} }}
                '''

            def extract_page(self, data: dict) -> tuple[list[dict], str | None]:
                conn = data["repository"]["issues"]
                cursor = conn["pageInfo"]["endCursor"] if conn["pageInfo"]["hasNextPage"] else None
                return conn["nodes"], cursor

        # extract_records is handled automatically via fetch_all — don't override it.
    """

    query: str = ""  # unused in paginated mode

    @abc.abstractmethod
    def build_query(self, cursor: str | None) -> str: ...

    @abc.abstractmethod
    def extract_page(self, data: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]: ...

    def extract_records(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError("Use build_query / extract_page for paginated assets.")

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


class BaseDbReplicationAsset(abc.ABC):
    """Base for incremental DB replication assets.

    Reads connection credentials via the ``secret_resolver`` Dagster resource.
    Secrets must be registered as ``DAGSTER__<ENGINE_NAME>__URI`` and
    ``DAGSTER__<ENGINE_NAME>__SINCE`` (when using ``DevEnvSecretResolver``).

    Usage::

        class PostgresOrders(BaseDbReplicationAsset):
            engine_name = "postgres"
            table = "orders"

            def get_query(self, since: str) -> str:
                return "SELECT * FROM orders WHERE updated_at >= :since"

        @asset(group_name="db_replication", required_resource_keys={"secret_resolver"})
        def replicate_postgres_orders(context: AssetExecutionContext) -> str:
            return PostgresOrders().materialize(context)
    """

    engine_name: str
    table: str
    output_root: pathlib.Path = pathlib.Path("tmp")

    @abc.abstractmethod
    def get_query(self, since: str) -> str:
        """Return the SQL with a ``:since`` bind parameter for the watermark."""
        ...

    def materialize(self, context: AssetExecutionContext) -> str:
        try:
            from sqlalchemy import create_engine, text
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "DB replication requires sqlalchemy and pandas.\n"
                'Install with:  pip install "pr-automation-agent[dagster]"'
            ) from exc

        resolver: AbstractSecretResolver = context.resources.secret_resolver
        uri = resolver.resolve_as_str(SecretReference(self.engine_name.upper(), "URI"))
        since = resolver.resolve_as_str(SecretReference(self.engine_name.upper(), "SINCE"))

        eng = create_engine(uri)
        df = pd.read_sql(text(self.get_query(since)), eng, params={"since": since})

        out = self.output_root / self.engine_name / self.table
        out.mkdir(parents=True, exist_ok=True)
        fp = out / f"{dt.date.today().isoformat()}.parquet"
        df.to_parquet(fp, index=False)

        context.add_output_metadata({
            "rows": MetadataValue.int(len(df)),
            "path": MetadataValue.path(str(fp)),
        })
        return str(fp)
