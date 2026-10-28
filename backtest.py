from collections.abc import Callable

from paper_trading import PaperPortfolio, RiskLimits


def run_backtest(rows: list[dict], strategy: Callable[[dict], dict], starting_cash: float = 1000.0, risk_limits: RiskLimits | None = None, fee_per_contract: float = 0.0, slippage: float = 0.0, maximum_drawdown: float | None = None) -> dict:
    portfolio = PaperPortfolio(starting_cash, risk_limits=risk_limits, fee_per_contract=fee_per_contract)
    prices = {}
    equity_curve = []
    order_errors = []
    peak_equity = starting_cash
    trading_halted = False

    for row in rows:
        ticker = row.get("ticker")
        mid = row.get("mid")
        bid = row.get("bid")
        ask = row.get("ask")

        if not isinstance(ticker, str):
            continue
        if not isinstance(mid, (int, float)):
            continue

        prices[ticker] = mid
        outcome = row.get("outcome")
        is_settlement = row.get("is_settlement") is True

        if is_settlement and outcome in (0, 1) and ticker in portfolio.positions:
            quantity_to_settle = portfolio.positions[ticker].quantity
            portfolio.sell(ticker, quantity_to_settle, float(outcome))
            prices[ticker] = float(outcome)
            signal = {"action": "hold", "quantity": 0}
        else:
            current_equity = portfolio.equity(prices)
            if current_equity > peak_equity:
                peak_equity = current_equity

            current_drawdown = peak_equity - current_equity
            if maximum_drawdown is not None and current_drawdown >= maximum_drawdown:
                trading_halted = True

            if trading_halted:
                signal = {"action": "hold", "quantity": 0}
            else:
                strategy_row = dict(row)
                strategy_row.pop("outcome", None)
                strategy_row.pop("is_settlement", None)
                signal = strategy(strategy_row)
        action = signal.get("action", "hold")
        quantity = signal.get("quantity", 0)

        try:
            if action == "buy" and isinstance(ask, (int, float)):
                buy_price = min(1.0, ask + slippage)
                portfolio.buy(ticker, quantity, buy_price)
            elif action == "sell" and isinstance(bid, (int, float)):
                sell_price = max(0.0, bid - slippage)
                portfolio.sell(ticker, quantity, sell_price)
        except ValueError as error:
            order_errors.append({
                "ticker": ticker,
                "action": action,
                "error": str(error),
            })

        equity_curve.append({
            "timestamp": row.get("fetched_at"),
            "equity": portfolio.equity(prices),
            "cash": portfolio.cash,
        })

    final_equity = portfolio.equity(prices)
    peak_equity = starting_cash
    measured_maximum_drawdown = 0.0

    for point in equity_curve:
        if point["equity"] > peak_equity:
            peak_equity = point["equity"]

        drawdown = peak_equity - point["equity"]
        if drawdown > measured_maximum_drawdown:
            measured_maximum_drawdown = drawdown

    return {
        "starting_cash": starting_cash,
        "final_equity": final_equity,
        "return": final_equity - starting_cash,
        "realized_profit": portfolio.realized_profit,
        "maximum_drawdown": measured_maximum_drawdown,
        "equity_curve": equity_curve,
        "order_errors": order_errors,
        "trading_halted": trading_halted,
    }

