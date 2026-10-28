import time

import requests
URL = "https://external-api.kalshi.com/trade-api/v2"
request_count = 0


def _get_json(url: str, params: dict) -> dict:
    global request_count
    last_error = None

    for attempt in range(3):
        request_count += 1
        print("request", request_count, url, params, flush=True)
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            last_error = error
            if attempt < 2:
                time.sleep(2 ** attempt)

    if last_error is not None:
        raise last_error

    raise RuntimeError("request failed without an error")


def get_markets(limit: int | None = None, status: str = "open") -> list[dict]:
    if limit is not None and limit <= 0:
        return []

    url = URL + "/markets"

    allMarkets = []
    cursor = None
    while True:
        if limit is None:
            page_limit = 100
        else:
            page_limit = min(100, limit - len(allMarkets))

        paramsM = {"limit": page_limit, "status": status}
        if cursor:
            paramsM["cursor"] = cursor


        data = _get_json(url, paramsM)
        markets = data["markets"]
        allMarkets.extend(markets)

        cursor = data.get("cursor")

        if not cursor or limit is not None and len(allMarkets) >= limit:
            break

    if limit is None:
        return allMarkets

    return allMarkets[:limit]


def get_settled_markets(limit: int | None = None) -> list[dict]:
    return get_markets(limit=limit, status="settled")


def get_market_trades(ticker: str | None = None, limit: int | None = None) -> list[dict]:
    if limit is not None and limit <= 0:
        return []

    url = URL + "/markets/trades"

    allTrades = []
    cursor = None
    while True:
        if limit is None:
            page_limit = 100
        else:
            page_limit = min(100, limit - len(allTrades))

        paramsT = {"limit": page_limit}
        if ticker:
            paramsT["ticker"] = ticker
        if cursor:
            paramsT["cursor"] = cursor

        data = _get_json(url, paramsT)
        trades = data["trades"]
        allTrades.extend(trades)

        cursor = data.get("cursor")

        if not cursor or limit is not None and len(allTrades) >= limit:
            break

    if limit is None:
        return allTrades

    return allTrades[:limit]


def get_market_orderbook(ticker: str, depth: int | None = None) -> dict:
    url = URL + "/markets/" + ticker + "/orderbook"
    params = {}

    if depth is not None:
        params["depth"] = depth

    return _get_json(url, params)



