from backtest import run_backtest
from kalshi_client import get_settled_markets
from ml_strategy import make_probability_strategy
from probability_model import fit_logistic_model
from research_data import build_backtest_rows, load_snapshots


def main():
    feature_snapshots = load_snapshots()
    settled_markets = get_settled_markets()
    rows = build_backtest_rows(feature_snapshots, settled_markets)

    train_end = int(len(rows) * 0.6)
    validation_end = int(len(rows) * 0.8)
    if train_end <= 0 or validation_end <= train_end or validation_end >= len(rows):
        raise ValueError("rows must contain enough data for train, validation, and test periods")

    train_rows = rows[:train_end]
    validation_rows = rows[train_end:validation_end]
    test_rows = rows[validation_end:]
    model_rows = [row for row in train_rows if row.get("is_settlement") is not True]
    feature_names = [
        "probability",
        "spread",
        "volume",
        "volume_24h",
        "liquidity",
        "hours_until_expiration",
    ]
    model = fit_logistic_model(model_rows, feature_names)

    validation_strategy = make_probability_strategy(model, minimum_edge=0.05)
    validation_report = run_backtest(validation_rows, validation_strategy, fee_per_contract=0.01, slippage=0.01)

    test_strategy = make_probability_strategy(model, minimum_edge=0.05)
    test_report = run_backtest(test_rows, test_strategy, fee_per_contract=0.01, slippage=0.01)

    print("usable backtest rows:", len(rows))
    print("validation report:", validation_report)
    print("test report:", test_report)


if __name__ == "__main__":
    main()

