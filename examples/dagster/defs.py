"""Dagster Definitions for the pr-automation-agent examples.

    dagster asset list -m examples.dagster.defs
    dagster asset materialize --select fetch_jsonplaceholder_posts -m examples.dagster.defs
"""

from dagster import Definitions, load_assets_from_modules
from pr_automation_agent.integrations.dagster import dev_env_secret_resolver_resource

import examples.dagster.rest.jsonplaceholder.posts_asset as rest_posts
import examples.dagster.graphql.countries.countries_asset as gql_countries
import examples.dagster.db.postgres.orders_replication_asset as db_orders

all_assets = load_assets_from_modules([rest_posts, gql_countries, db_orders])

defs = Definitions(
    assets=all_assets,
    resources={"secret_resolver": dev_env_secret_resolver_resource},
)
