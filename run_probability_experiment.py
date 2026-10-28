from kalshi_client import get_settled_markets
from ml_experiment import run_probability_experiment
from research_data import build_calibration_rows, load_snapshots


def main():
    feature_snapshots = load_snapshots()
    settled_markets = get_settled_markets()
    rows = build_calibration_rows(feature_snapshots, settled_markets)
    feature_names = [
        "probability",
        "spread",
        "volume",
        "volume_24h",
        "liquidity",
        "hours_until_expiration",
    ]
    report = run_probability_experiment(rows, feature_names)

    print("usable research rows:", len(rows))
    print("train report:", report["train"])
    print("validation report:", report["validation"])
    print("test report:", report["test"])


if __name__ == "__main__":
    main()

