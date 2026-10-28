import json
from datetime import datetime
from pathlib import Path


def load_snapshots(directory: str = "data", prefix: str = "features_") -> list[dict]:
    data_directory = Path(directory)
    snapshot_paths = sorted(data_directory.glob(prefix + "*.json"))
    snapshots = []

    for snapshot_path in snapshot_paths:
        with snapshot_path.open("r", encoding="utf-8") as file:
            snapshots.append(json.load(file))

    return snapshots


def build_calibration_rows(feature_snapshots: list[dict], settled_markets: list[dict]) -> list[dict]:
    outcomes = {}
    for market in settled_markets:
        ticker = market.get("ticker")
        result = market.get("result")

        if result == "yes":
            outcomes[ticker] = 1
        elif result == "no":
            outcomes[ticker] = 0

    rows = []
    for snapshot in feature_snapshots:
        fetched_at = snapshot.get("fetched_at")
        features = snapshot.get("features", [])

        for feature in features:
            ticker = feature.get("ticker")
            probability = feature.get("mid")

            if ticker not in outcomes:
                continue
            if not isinstance(probability, (int, float)):
                continue
            if probability < 0 or probability > 1:
                continue

            rows.append({
                "fetched_at": fetched_at,
                "ticker": ticker,
                "probability": probability,
                "outcome": outcomes[ticker],
                "spread": feature.get("spread"),
                "volume": feature.get("volume"),
                "volume_24h": feature.get("volume_24h"),
                "liquidity": feature.get("liquidity"),
                "hours_until_expiration": feature.get("hours_until_expiration"),
            })

    return rows


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or value == "":
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def build_backtest_rows(feature_snapshots: list[dict], settled_markets: list[dict]) -> list[dict]:
    settled_data = {}
    for market in settled_markets:
        ticker = market.get("ticker")
        result = market.get("result")
        settlement_time = _parse_time(market.get("settlement_ts"))

        if result not in ("yes", "no") or settlement_time is None:
            continue

        outcome = 1 if result == "yes" else 0
        settled_data[ticker] = {"outcome": outcome, "settlement_time": settlement_time}

    observations = {}
    for snapshot in feature_snapshots:
        fetched_at = _parse_time(snapshot.get("fetched_at"))
        if fetched_at is None:
            continue

        for feature in snapshot.get("features", []):
            ticker = feature.get("ticker")
            if ticker not in settled_data:
                continue

            if not isinstance(feature.get("mid"), (int, float)):
                continue

            row = dict(feature)
            row["fetched_at"] = fetched_at.isoformat()
            row["probability"] = feature.get("mid")
            row["outcome"] = settled_data[ticker]["outcome"]
            row["is_settlement"] = False
            observations.setdefault(ticker, []).append(row)

    rows = []
    for ticker, ticker_rows in observations.items():
        settlement_time = settled_data[ticker]["settlement_time"]
        rows.extend(ticker_rows)

        rows_before_settlement = []
        for row in ticker_rows:
            row_time = _parse_time(row.get("fetched_at"))
            if row_time is not None and row_time <= settlement_time:
                rows_before_settlement.append(row)

        if not rows_before_settlement:
            continue

        last_row = dict(rows_before_settlement[-1])
        outcome = settled_data[ticker]["outcome"]
        settlement_price = float(outcome)
        last_row["fetched_at"] = settlement_time.isoformat()
        last_row["bid"] = settlement_price
        last_row["ask"] = settlement_price
        last_row["mid"] = settlement_price
        last_row["probability"] = settlement_price
        last_row["is_settlement"] = True
        rows.append(last_row)

    rows.sort(key=lambda row: row["fetched_at"])
    return rows

