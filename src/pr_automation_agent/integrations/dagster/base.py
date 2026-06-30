"""Dagster-specific wrappers that add ``materialize(context)`` to the core fetchers."""

from dagster import AssetExecutionContext, MetadataValue

from pr_automation_agent.base import (
    BaseRestFetcher as _CoreRestFetcher,
    BaseGraphQLFetcher as _CoreGraphQLFetcher,
    PaginatedGraphQLFetcher as _CorePaginatedGraphQLFetcher,
    BaseDbReplicator as _CoreDbReplicator,
)


class BaseRestAsset(_CoreRestFetcher):
    """Dagster asset base for REST ingest. Subclass and implement ``fetch_all()``.

    Usage::

        from pr_automation_agent.integrations.dagster import BaseRestAsset
        from dagster import asset, AssetExecutionContext

        class StripeInvoices(BaseRestAsset):
            provider = "stripe"
            entity = "invoices"

            def fetch_all(self) -> list[dict]:
                import requests
                r = requests.get("https://api.stripe.com/v1/invoices", timeout=60)
                r.raise_for_status()
                return r.json()["data"]

        @asset(group_name="rest_crawl")
        def fetch_stripe_invoices(context: AssetExecutionContext) -> str:
            return StripeInvoices().materialize(context)
    """

    def materialize(self, context: AssetExecutionContext) -> str:
        path, rows = self.run()
        context.add_output_metadata({
            "rows": MetadataValue.int(rows),
            "path": MetadataValue.path(path),
        })
        return path


class BaseGraphQLAsset(_CoreGraphQLFetcher):
    """Dagster asset base for GraphQL ingest. Subclass and implement ``extract_records()``."""

    def materialize(self, context: AssetExecutionContext) -> str:
        path, rows = self.run()
        context.add_output_metadata({
            "rows": MetadataValue.int(rows),
            "path": MetadataValue.path(path),
        })
        return path


class PaginatedGraphQLAsset(_CorePaginatedGraphQLFetcher):
    """Dagster asset base for cursor-paginated GraphQL. Implement ``build_query`` + ``extract_page``."""

    def materialize(self, context: AssetExecutionContext) -> str:
        path, rows = self.run()
        context.add_output_metadata({
            "rows": MetadataValue.int(rows),
            "path": MetadataValue.path(path),
        })
        return path


class BaseDbReplicationAsset(_CoreDbReplicator):
    """Dagster asset base for DB replication. Resolver comes from ``context.resources.secret_resolver``.

    Usage::

        from pr_automation_agent.integrations.dagster import BaseDbReplicationAsset
        from dagster import asset, AssetExecutionContext

        class PostgresOrders(BaseDbReplicationAsset):
            engine_name = "postgres"
            table = "orders"

            def get_query(self, since: str) -> str:
                return "SELECT * FROM orders WHERE updated_at >= :since"

        @asset(group_name="db_replication", required_resource_keys={"secret_resolver"})
        def replicate_postgres_orders(context: AssetExecutionContext) -> str:
            return PostgresOrders().materialize(context)
    """

    def materialize(self, context: AssetExecutionContext) -> str:
        path, rows = self._run_with_resolver(context.resources.secret_resolver)
        context.add_output_metadata({
            "rows": MetadataValue.int(rows),
            "path": MetadataValue.path(path),
        })
        return path
