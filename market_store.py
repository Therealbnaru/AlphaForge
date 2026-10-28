import json
from datetime import datetime, timezone
from pathlib import Path


def save_market_snapshot(markets: list[dict], directory: str = "data") -> Path:
    data_directory = Path(directory)
    data_directory.mkdir(exist_ok=True)

    fetched_at = datetime.now(timezone.utc)
    file_name = fetched_at.strftime("markets_%Y%m%dT%H%M%SZ.json")
    file_path = data_directory / file_name

    snapshot = {
        "fetched_at": fetched_at.isoformat(),
        "markets": markets,
    }

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2, ensure_ascii=False)

    return file_path


def save_feature_snapshot(features: list[dict], directory: str = "data") -> Path:
    data_directory = Path(directory)
    data_directory.mkdir(exist_ok=True)

    fetched_at = datetime.now(timezone.utc)
    file_name = fetched_at.strftime("features_%Y%m%dT%H%M%SZ.json")
    file_path = data_directory / file_name

    snapshot = {
        "fetched_at": fetched_at.isoformat(),
        "features": features,
    }

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2, ensure_ascii=False)

    return file_path


def save_trade_snapshot(trades: list[dict], directory: str = "data") -> Path:
    data_directory = Path(directory)
    data_directory.mkdir(exist_ok=True)

    fetched_at = datetime.now(timezone.utc)
    file_name = fetched_at.strftime("trades_%Y%m%dT%H%M%SZ.json")
    file_path = data_directory / file_name

    snapshot = {
        "fetched_at": fetched_at.isoformat(),
        "trades": trades,
    }

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2, ensure_ascii=False)

    return file_path


def save_orderbook_snapshot(orderbooks: list[dict], directory: str = "data") -> Path:
    data_directory = Path(directory)
    data_directory.mkdir(exist_ok=True)

    fetched_at = datetime.now(timezone.utc)
    file_name = fetched_at.strftime("orderbooks_%Y%m%dT%H%M%SZ.json")
    file_path = data_directory / file_name

    snapshot = {
        "fetched_at": fetched_at.isoformat(),
        "orderbooks": orderbooks,
    }

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2, ensure_ascii=False)

    return file_path

