from datetime import datetime, timezone


def read_number(value: object) -> float | None:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def hours_until(value: object) -> float | None:
    if not isinstance(value, str) or value == "":
        return None

    try:
        expiration_time = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if expiration_time.tzinfo is None:
        expiration_time = expiration_time.replace(tzinfo=timezone.utc)

    current_time = datetime.now(timezone.utc)
    seconds_until_expiration = (expiration_time - current_time).total_seconds()

    return seconds_until_expiration / 3600


def build_market_features(markets: list[dict]) -> list[dict]:
    features = []

    for market in markets:
        bid = read_number(market.get("yes_bid_dollars"))
        ask = read_number(market.get("yes_ask_dollars"))

        mid = None
        spread = None
        if bid is not None and ask is not None:
            mid = (bid + ask) / 2
            spread = ask - bid

        feature = {
            "ticker": market.get("ticker"),
            "event_ticker": market.get("event_ticker"),
            "series_ticker": market.get("series_ticker"),
            "category": market.get("category", "unknown"),
            "title": market.get("title"),
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "spread": spread,
            "last_price": read_number(market.get("last_price_dollars")),
            "volume": read_number(market.get("volume_fp")),
            "volume_24h": read_number(market.get("volume_24h_fp")),
            "liquidity": read_number(market.get("liquidity_dollars")),
            "hours_until_expiration": hours_until(market.get("expiration_time")),
        }
        features.append(feature)

    return features


def build_orderbook_features(orderbook: dict) -> dict:
    orderbook_data = orderbook.get("orderbook_fp", {})
    yes_levels = orderbook_data.get("yes_dollars", [])
    no_levels = orderbook_data.get("no_dollars", [])

    yes_depth = 0.0
    no_depth = 0.0
    best_yes_bid = None
    best_no_bid = None

    for level in yes_levels:
        if len(level) != 2:
            continue

        price = read_number(level[0])
        quantity = read_number(level[1])
        if price is None or quantity is None:
            continue

        yes_depth += quantity
        if best_yes_bid is None or price > best_yes_bid:
            best_yes_bid = price

    for level in no_levels:
        if len(level) != 2:
            continue

        price = read_number(level[0])
        quantity = read_number(level[1])
        if price is None or quantity is None:
            continue

        no_depth += quantity
        if best_no_bid is None or price > best_no_bid:
            best_no_bid = price

    total_depth = yes_depth + no_depth
    depth_imbalance = None
    if total_depth > 0:
        depth_imbalance = (yes_depth - no_depth) / total_depth

    yes_ask = None
    if best_no_bid is not None:
        yes_ask = 1 - best_no_bid

    spread = None
    if best_yes_bid is not None and yes_ask is not None:
        spread = yes_ask - best_yes_bid

    return {
        "best_yes_bid": best_yes_bid,
        "best_yes_ask": yes_ask,
        "yes_depth": yes_depth,
        "no_depth": no_depth,
        "depth_imbalance": depth_imbalance,
        "spread": spread,
    }

