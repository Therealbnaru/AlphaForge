from calibration import evaluate_calibration
from kalshi_client import get_settled_markets
from research_data import build_calibration_rows, load_snapshots


def main():
    feature_snapshots = load_snapshots()
    settled_markets = get_settled_markets()
    rows = build_calibration_rows(feature_snapshots, settled_markets)
    report = evaluate_calibration(rows)

    print("feature snapshots:", len(feature_snapshots))
    print("settled markets:", len(settled_markets))
    print("usable calibration rows:", report["count"])
    print("brier score:", report["brier_score"])
    print("log loss:", report["log_loss"])


if __name__ == "__main__":
    main()

