from dagster import Definitions, load_assets_from_modules, resource

import warehouse.oso_dagster.assets.ingest.rest.jsonplaceholder.posts_asset as rest_mod
import warehouse.oso_dagster.assets.ingest.graphql.countries.countries_asset as gql_mod
import warehouse.oso_dagster.assets.ingest.db.postgres.orders_replication_asset as db_mod

from pr_automation_agent import DevEnvSecretResolver


@resource
def secret_resolver():
    return DevEnvSecretResolver()


assets = load_assets_from_modules([rest_mod, gql_mod, db_mod])

defs = Definitions(
    assets=assets,
    resources={"secret_resolver": secret_resolver},
)
