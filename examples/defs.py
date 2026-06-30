"""Production Dagster Definitions for pr-automation-agent examples.

Point Dagster at this module to list or materialize the example assets:

    dagster asset list -m examples.defs
    dagster asset materialize --select fetch_jsonplaceholder_posts -m examples.defs

To adapt for your own repo:
  1. Copy the asset files you need into your ingest directory.
  2. Import your modules here (or use load_assets_from_package_module).
  3. Replace dev_env_secret_resolver_resource with your production secret backend.
"""

from dagster import Definitions, load_assets_from_modules

from pr_automation_agent import dev_env_secret_resolver_resource

import examples.rest.jsonplaceholder.posts_asset as rest_posts
import examples.graphql.countries.countries_asset as gql_countries
import examples.db.postgres.orders_replication_asset as db_orders

all_assets = load_assets_from_modules([rest_posts, gql_countries, db_orders])

defs = Definitions(
    assets=all_assets,
    resources={"secret_resolver": dev_env_secret_resolver_resource},
)
