#!/usr/bin/env python3
"""
Section IV.D — PyPI EU Download Share (E3 Jurisdictional Scoping)
Queries bigquery-public-data.pypi.file_downloads for EU-27 download share
across the 25 packages in the E3 study population.
"""

import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account

KEY_FILE = "/Users/apple/Downloads/pr-automation-501712-4666cdba9f6b.json"

EU_27 = {
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
}

PACKAGES = {
    'Scientific computing': ['numpy', 'pandas', 'scipy', 'scikit-learn', 'matplotlib'],
    'Web / API frameworks': ['requests', 'fastapi', 'flask', 'httpx', 'aiohttp'],
    'Developer tooling':    ['black', 'ruff', 'pytest', 'mypy', 'rich'],
    'Data engineering':     ['dagster', 'prefect', 'apache-airflow', 'dbt-core', 'great-expectations'],
    'AI / LLM tooling':     ['langchain', 'openai', 'anthropic', 'transformers', 'datasets'],
}

ALL_PACKAGES = [p for pkgs in PACKAGES.values() for p in pkgs]

QUERY = """
SELECT
  file.project AS package,
  UPPER(country_code) AS country_code,
  COUNT(*) AS downloads
FROM `bigquery-public-data.pypi.file_downloads`
WHERE
  DATE(timestamp) = DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)
  AND LOWER(file.project) IN UNNEST(@packages)
GROUP BY package, country_code
ORDER BY package, downloads DESC
"""

def main():
    creds = service_account.Credentials.from_service_account_file(
        KEY_FILE,
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    # Extract project ID from key file
    with open(KEY_FILE) as f:
        project_id = json.load(f)['project_id']

    client = bigquery.Client(credentials=creds, project=project_id)

    print("Running BigQuery query (scanning ~30 days of PyPI download data)...")
    print("This may take 30–90 seconds.\n")

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("packages", "STRING",
                                         [p.lower() for p in ALL_PACKAGES])
        ]
    )

    results = client.query(QUERY, job_config=job_config).result()

    # Aggregate per package
    pkg_data = {p: {'total': 0, 'eu': 0} for p in ALL_PACKAGES}
    for row in results:
        pkg = row.package.lower()
        # normalise package name (PyPI uses hyphens, results may vary)
        for p in ALL_PACKAGES:
            if pkg == p or pkg == p.replace('-', '_'):
                pkg = p
                break
        if pkg not in pkg_data:
            continue
        downloads = row.downloads
        pkg_data[pkg]['total'] += downloads
        if row.country_code in EU_27:
            pkg_data[pkg]['eu'] += downloads

    # Print TABLE VI
    print("=" * 75)
    print("TABLE VI: EU-27 Download Share for E3 Packages (1-day window)")
    print("=" * 75)
    print(f"{'Category':<24} {'Package':<22} {'Total DLs':>12} {'EU-27 DLs':>12} {'EU Share':>9} {'In-scope'}")
    print("-" * 88)

    grand_total = 0
    grand_eu = 0
    rows_for_paper = []

    for category, pkgs in PACKAGES.items():
        cat_total = sum(pkg_data[p]['total'] for p in pkgs)
        cat_eu = sum(pkg_data[p]['eu'] for p in pkgs)
        for p in pkgs:
            total = pkg_data[p]['total']
            eu = pkg_data[p]['eu']
            share = eu / total * 100 if total > 0 else 0
            in_scope = 'Yes' if share >= 5.0 else 'No'
            print(f"  {category:<22} {p:<22} {total:>12,} {eu:>12,} {share:>8.1f}% {in_scope}")
            rows_for_paper.append({
                'category': category,
                'package': p,
                'total': total,
                'eu': eu,
                'share': round(share, 1),
                'in_scope': in_scope
            })
        grand_total += cat_total
        grand_eu += cat_eu
        print()

    grand_share = grand_eu / grand_total * 100 if grand_total > 0 else 0
    print("-" * 88)
    print(f"  {'TOTAL':<22} {'25 packages':<22} {grand_total:>12,} {grand_eu:>12,} {grand_share:>8.1f}%")
    print()

    # Save
    output = {
        'summary': {
            'total_downloads': grand_total,
            'eu_downloads': grand_eu,
            'eu_share_pct': round(grand_share, 2),
            'packages_in_scope': sum(1 for r in rows_for_paper if r['in_scope'] == 'Yes'),
        },
        'packages': rows_for_paper
    }
    out_path = '/Users/apple/pr-automation-agent/tmp/pypi_eu_results.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {out_path}")

if __name__ == '__main__':
    main()
