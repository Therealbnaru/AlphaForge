import argparse
import json
import sqlite3


TABLES = [
    "market_snapshots",
    "feature_snapshots",
    "trades",
    "orderbook_snapshots",
]


def _table_report(connection: sqlite3.Connection, table: str) -> dict:
    count = connection.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
    distinct_markets = connection.execute(
        "SELECT COUNT(DISTINCT ticker) FROM " + table
    ).fetchone()[0]
    oldest = connection.execute(
        "SELECT MIN(observed_at) FROM " + table
    ).fetchone()[0]
    newest = connection.execute(
        "SELECT MAX(observed_at) FROM " + table
    ).fetchone()[0]

    return {
        "count": count,
        "distinct_markets": distinct_markets,
        "oldest_observation": oldest,
        "newest_observation": newest,
    }


def build_data_quality_report(database_path: str = "data/alphaforge.db") -> dict:
    connection = sqlite3.connect(database_path)

    try:
        report = {"tables": {}}
        for table in TABLES:
            report["tables"][table] = _table_report(connection, table)

        feature_count = report["tables"]["feature_snapshots"]["count"]
        missing_mid = connection.execute(
            "SELECT COUNT(*) FROM feature_snapshots WHERE mid IS NULL"
        ).fetchone()[0]
        missing_spread = connection.execute(
            "SELECT COUNT(*) FROM feature_snapshots WHERE spread IS NULL"
        ).fetchone()[0]

        report["feature_completeness"] = {
            "rows": feature_count,
            "missing_mid": missing_mid,
            "missing_spread": missing_spread,
        }
        report["ready_for_research"] = feature_count >= 100
        return report
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description="Inspect AlphaForge data quality.")
    parser.add_argument("--database", default="data/alphaforge.db")
    arguments = parser.parse_args()
    report = build_data_quality_report(arguments.database)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

