import time

from kalshi_client import get_market_orderbook, get_market_trades, get_markets
from market_features import build_market_features, read_number
from market_store import save_feature_snapshot, save_market_snapshot, save_orderbook_snapshot, save_trade_snapshot
from research_database import ResearchDatabase


def _volume_for_sorting(market: dict) -> float:
    volume = read_number(market.get("volume_24h_fp"))
    if volume is None:
        return 0.0
    return volume


def choose_microstructure_markets(markets: list[dict], count: int) -> list[dict]:
    if count <= 0:
        return []

    ordered_markets = sorted(markets, key=_volume_for_sorting, reverse=True)
    return ordered_markets[:count]


def collect_once(directory: str = "data", microstructure_count: int = 10, trade_limit: int = 100, market_limit: int | None = None) -> dict:
    print("starting collection cycle", flush=True)
    markets = get_markets(limit=market_limit)
    print("market scan complete:", len(markets), flush=True)
    features = build_market_features(markets)
    market_path = save_market_snapshot(markets, directory)
    feature_path = save_feature_snapshot(features, directory)

    selected_markets = choose_microstructure_markets(markets, microstructure_count)
    trades = []
    orderbooks = []
    errors = []

    for market in selected_markets:
        ticker = market.get("ticker")
        if not isinstance(ticker, str):
            continue

        try:
            market_trades = get_market_trades(ticker=ticker, limit=trade_limit)
            trades.extend(market_trades)
        except Exception as error:
            errors.append({"ticker": ticker, "source": "trades", "error": str(error)})

        try:
            orderbook = get_market_orderbook(ticker)
            orderbooks.append({"ticker": ticker, "orderbook": orderbook})
        except Exception as error:
            errors.append({"ticker": ticker, "source": "orderbook", "error": str(error)})

    trade_path = save_trade_snapshot(trades, directory)
    orderbook_path = save_orderbook_snapshot(orderbooks, directory)

    with ResearchDatabase(directory) as database:
        database_path = str(database.path)
        database.save_markets(markets)
        database.save_features(features)
        database.save_trades(trades)
        database.save_orderbooks(orderbooks)

    return {
        "market_count": len(markets),
        "feature_count": len(features),
        "selected_count": len(selected_markets),
        "trade_count": len(trades),
        "orderbook_count": len(orderbooks),
        "errors": errors,
        "market_path": str(market_path),
        "feature_path": str(feature_path),
        "trade_path": str(trade_path),
        "orderbook_path": str(orderbook_path),
        "database_path": database_path,
    }


def run_collector(interval_seconds: int = 60, iterations: int | None = None, directory: str = "data", microstructure_count: int = 10, trade_limit: int = 100, market_limit: int | None = None) -> None:
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")
    if iterations is not None and iterations <= 0:
        raise ValueError("iterations must be positive when provided")

    completed_iterations = 0
    try:
        while iterations is None or completed_iterations < iterations:
            summary = collect_once(directory, microstructure_count, trade_limit, market_limit)
            print(summary, flush=True)
            completed_iterations += 1

            if iterations is None or completed_iterations < iterations:
                time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("data collector stopped")

