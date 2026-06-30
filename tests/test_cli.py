import pathlib
import pytest
from click.testing import CliRunner
from pr_automation_agent.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Plain Python (default — no --framework)
# ---------------------------------------------------------------------------

def test_scaffold_rest_plain_creates_file(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "stripe", "--entity", "invoices", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    dest = tmp_path / "rest" / "stripe" / "invoices_asset.py"
    assert dest.exists()
    content = dest.read_text()
    assert "fetch_stripe_invoices" in content
    assert "BaseRestFetcher" in content
    assert "EU AI Act Art. 52" in content
    assert "if __name__" in content          # plain Python entry point
    assert "AssetExecutionContext" not in content   # no Dagster


def test_scaffold_graphql_plain_creates_file(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "graphql", "--provider", "github", "--entity", "issues", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    dest = tmp_path / "graphql" / "github" / "issues_asset.py"
    assert dest.exists()
    content = dest.read_text()
    assert "BaseGraphQLFetcher" in content
    assert "AssetExecutionContext" not in content


def test_scaffold_db_plain_creates_file(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "db", "--engine", "postgres", "--table", "orders", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    dest = tmp_path / "db" / "postgres" / "orders_replication_asset.py"
    assert dest.exists()
    content = dest.read_text()
    assert "BaseDbReplicator" in content
    assert "PR_AGENT__POSTGRES" in content


# ---------------------------------------------------------------------------
# Dagster (--framework dagster)
# ---------------------------------------------------------------------------

def test_scaffold_rest_dagster_creates_file(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "stripe", "--entity", "invoices",
         "--framework", "dagster", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    dest = tmp_path / "rest" / "stripe" / "invoices_asset.py"
    assert dest.exists()
    content = dest.read_text()
    assert "BaseRestAsset" in content
    assert "integrations.dagster" in content
    assert "AssetExecutionContext" in content
    assert "if __name__" not in content      # no plain Python entry point


def test_scaffold_db_dagster_creates_file(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "db", "--engine", "postgres", "--table", "orders",
         "--framework", "dagster", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    content = (tmp_path / "db" / "postgres" / "orders_replication_asset.py").read_text()
    assert "BaseDbReplicationAsset" in content
    assert "required_resource_keys" in content


# ---------------------------------------------------------------------------
# Shared behaviour
# ---------------------------------------------------------------------------

def test_scaffold_dry_run_prints_without_writing(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "myapi", "--entity", "products",
         "--output-dir", str(tmp_path), "--dry-run"],
    )
    assert result.exit_code == 0, result.output
    assert "fetch_myapi_products" in result.output
    assert not (tmp_path / "rest").exists()


def test_scaffold_rest_missing_provider_errors(runner, tmp_path):
    result = runner.invoke(
        cli, ["scaffold", "rest", "--entity", "invoices", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "--provider" in result.output


def test_scaffold_rest_missing_entity_errors(runner, tmp_path):
    result = runner.invoke(
        cli, ["scaffold", "rest", "--provider", "stripe", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "--entity" in result.output


def test_scaffold_db_missing_engine_errors(runner, tmp_path):
    result = runner.invoke(
        cli, ["scaffold", "db", "--table", "orders", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "--engine" in result.output


def test_scaffold_creates_init_files(runner, tmp_path):
    runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "acme", "--entity", "products", "--output-dir", str(tmp_path)],
    )
    assert (tmp_path / "__init__.py").exists()
    assert (tmp_path / "rest" / "__init__.py").exists()
    assert (tmp_path / "rest" / "acme" / "__init__.py").exists()


def test_scaffold_output_dir_gets_init_py(runner, tmp_path):
    runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "acme", "--entity", "orders", "--output-dir", str(tmp_path)],
    )
    assert (tmp_path / "__init__.py").exists()


def test_scaffold_provider_sanitised(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "My-API", "--entity", "Orders", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert (tmp_path / "rest" / "my_api" / "orders_asset.py").exists()
