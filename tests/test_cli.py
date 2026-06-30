import pathlib
import pytest
from click.testing import CliRunner
from pr_automation_agent.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_scaffold_rest_creates_file(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "stripe", "--entity", "invoices", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    dest = tmp_path / "rest" / "stripe" / "invoices_asset.py"
    assert dest.exists()
    content = dest.read_text()
    assert "fetch_stripe_invoices" in content
    assert "BaseRestAsset" in content
    assert "EU AI Act Art. 52" in content


def test_scaffold_graphql_creates_file(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "graphql", "--provider", "github", "--entity", "issues", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    dest = tmp_path / "graphql" / "github" / "issues_asset.py"
    assert dest.exists()
    content = dest.read_text()
    assert "fetch_github_issues" in content
    assert "BaseGraphQLAsset" in content


def test_scaffold_db_creates_file(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "db", "--engine", "postgres", "--table", "orders", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    dest = tmp_path / "db" / "postgres" / "orders_replication_asset.py"
    assert dest.exists()
    content = dest.read_text()
    assert "replicate_postgres_orders" in content
    assert "BaseDbReplicationAsset" in content


def test_scaffold_dry_run_prints_without_writing(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "myapi", "--entity", "products",
         "--output-dir", str(tmp_path), "--dry-run"],
    )
    assert result.exit_code == 0, result.output
    assert "fetch_myapi_products" in result.output
    assert not (tmp_path / "rest").exists()


def test_scaffold_rest_missing_entity_errors(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "stripe", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "--entity" in result.output


def test_scaffold_rest_missing_provider_errors(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--entity", "invoices", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "--provider" in result.output


def test_scaffold_output_dir_gets_init_py(runner, tmp_path):
    runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "acme", "--entity", "orders", "--output-dir", str(tmp_path)],
    )
    assert (tmp_path / "__init__.py").exists()


def test_scaffold_db_missing_engine_errors(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "db", "--provider", "mydb", "--table", "orders", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "--engine" in result.output


def test_scaffold_creates_init_files(runner, tmp_path):
    runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "acme", "--entity", "products", "--output-dir", str(tmp_path)],
    )
    assert (tmp_path / "rest" / "__init__.py").exists()
    assert (tmp_path / "rest" / "acme" / "__init__.py").exists()


def test_scaffold_provider_sanitised(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["scaffold", "rest", "--provider", "My-API", "--entity", "Orders", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    dest = tmp_path / "rest" / "my_api" / "orders_asset.py"
    assert dest.exists()
