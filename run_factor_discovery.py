from factor_discovery import discover_factors
from kalshi_client import get_settled_markets
from research_data import build_calibration_rows, load_snapshots


def main():
    feature_snapshots = load_snapshots()
    settled_markets = get_settled_markets()
    rows = build_calibration_rows(feature_snapshots, settled_markets)
    discoveries = discover_factors(rows)

    print("usable research rows:", len(rows))

    for discovery in discoveries:
        print(discovery)


if __name__ == "__main__":
    main()

