from backtest import run_backtest
from paper_trading import RiskLimits


def make_low_probability_strategy(threshold: float, quantity: float = 1.0):
    bought_tickers = set()

    def strategy(row: dict) -> dict:
        ticker = row.get("ticker")
        mid = row.get("mid")

        if ticker in bought_tickers:
            return {"action": "hold", "quantity": 0}
        if not isinstance(ticker, str) or not isinstance(mid, (int, float)):
            return {"action": "hold", "quantity": 0}
        if mid > threshold:
            return {"action": "hold", "quantity": 0}

        bought_tickers.add(ticker)
        return {"action": "buy", "quantity": quantity}

    return strategy


def search_low_probability_strategies(rows: list[dict], thresholds: list[float], starting_cash: float = 1000.0, risk_limits: RiskLimits | None = None, fee_per_contract: float = 0.0, slippage: float = 0.0) -> list[dict]:
    if not rows:
        return []
    if not thresholds:
        return []

    train_end = int(len(rows) * 0.6)
    validation_end = int(len(rows) * 0.8)
    if train_end <= 0 or validation_end <= train_end or validation_end >= len(rows):
        raise ValueError("rows must contain enough data for train, validation, and test periods")

    train_rows = rows[:train_end]
    validation_rows = rows[train_end:validation_end]
    test_rows = rows[validation_end:]
    candidates = []

    for threshold in thresholds:
        strategy = make_low_probability_strategy(threshold)
        train_report = run_backtest(train_rows, strategy, starting_cash, risk_limits, fee_per_contract, slippage)

        strategy = make_low_probability_strategy(threshold)
        validation_report = run_backtest(validation_rows, strategy, starting_cash, risk_limits, fee_per_contract, slippage)

        strategy = make_low_probability_strategy(threshold)
        test_report = run_backtest(test_rows, strategy, starting_cash, risk_limits, fee_per_contract, slippage)

        candidates.append({
            "threshold": threshold,
            "train_return": train_report["return"],
            "validation_return": validation_report["return"],
            "test_return": test_report["return"],
            "validation_maximum_drawdown": validation_report["maximum_drawdown"],
            "test_maximum_drawdown": test_report["maximum_drawdown"],
            "train_order_errors": len(train_report["order_errors"]),
            "validation_order_errors": len(validation_report["order_errors"]),
            "test_order_errors": len(test_report["order_errors"]),
        })

    candidates.sort(key=lambda candidate: candidate["validation_return"], reverse=True)
    return candidates

