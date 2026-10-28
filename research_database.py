import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _number(value: object) -> float | None:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _trade_key(trade: dict) -> str:
    trade_id = trade.get("trade_id", trade.get("id"))
    if isinstance(trade_id, str) and trade_id != "":
        return trade_id

    trade_text = json.dumps(trade, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(trade_text.encode("utf-8")).hexdigest()


class ResearchDatabase:
    def __init__(self, directory: str = "data"):
        data_directory = Path(directory)
        data_directory.mkdir(exist_ok=True)
        self.path = data_directory / "alphaforge.db"
        self.connection = sqlite3.connect(self.path)
        self._create_tables()

    def _create_tables(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS market_snapshots (
                observed_at TEXT NOT NULL,
                ticker TEXT NOT NULL,
                payload TEXT NOT NULL,
                PRIMARY KEY (observed_at, ticker)
            );

            CREATE TABLE IF NOT EXISTS feature_snapshots (
                observed_at TEXT NOT NULL,
                ticker TEXT NOT NULL,
                mid REAL,
                spread REAL,
                volume REAL,
                liquidity REAL,
                hours_until_expiration REAL,
                payload TEXT NOT NULL,
                PRIMARY KEY (observed_at, ticker)
            );

            CREATE TABLE IF NOT EXISTS trades (
                trade_key TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                ticker TEXT,
                trade_time TEXT,
                price REAL,
                quantity REAL,
                payload TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orderbook_snapshots (
                observed_at TEXT NOT NULL,
                ticker TEXT NOT NULL,
                payload TEXT NOT NULL,
                PRIMARY KEY (observed_at, ticker)
            );
            """
        )
        trade_columns = self.connection.execute("PRAGMA table_info(trades)").fetchall()
        column_names = {column[1] for column in trade_columns}
        if "trade_key" not in column_names:
            self.connection.execute("ALTER TABLE trades ADD COLUMN trade_key TEXT")
            self.connection.execute(
                "UPDATE trades SET trade_key = lower(hex(randomblob(16))) WHERE trade_key IS NULL"
            )

        self.connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS unique_trade_key ON trades (trade_key)"
        )
        self.connection.commit()

    def save_markets(self, markets: list[dict]) -> str:
        observed_at = datetime.now(timezone.utc).isoformat()
        records = []
        for market in markets:
            ticker = market.get("ticker")
            if isinstance(ticker, str):
                records.append((observed_at, ticker, json.dumps(market, ensure_ascii=False)))

        self.connection.executemany(
            "INSERT OR REPLACE INTO market_snapshots (observed_at, ticker, payload) VALUES (?, ?, ?)",
            records,
        )
        self.connection.commit()
        return observed_at

    def save_features(self, features: list[dict]) -> str:
        observed_at = datetime.now(timezone.utc).isoformat()
        records = []
        for feature in features:
            ticker = feature.get("ticker")
            if isinstance(ticker, str):
                records.append((
                    observed_at,
                    ticker,
                    _number(feature.get("mid")),
                    _number(feature.get("spread")),
                    _number(feature.get("volume")),
                    _number(feature.get("liquidity")),
                    _number(feature.get("hours_until_expiration")),
                    json.dumps(feature, ensure_ascii=False),
                ))

        self.connection.executemany(
            """
            INSERT OR REPLACE INTO feature_snapshots
            (observed_at, ticker, mid, spread, volume, liquidity, hours_until_expiration, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        self.connection.commit()
        return observed_at

    def save_trades(self, trades: list[dict]) -> str:
        observed_at = datetime.now(timezone.utc).isoformat()
        records = []
        for trade in trades:
            records.append((
                _trade_key(trade),
                observed_at,
                trade.get("ticker"),
                trade.get("created_time", trade.get("timestamp")),
                _number(trade.get("price_dollars", trade.get("price"))),
                _number(trade.get("count_fp", trade.get("quantity"))),
                json.dumps(trade, ensure_ascii=False),
            ))

        self.connection.executemany(
            "INSERT OR IGNORE INTO trades (trade_key, observed_at, ticker, trade_time, price, quantity, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            records,
        )
        self.connection.commit()
        return observed_at

    def save_orderbooks(self, orderbooks: list[dict]) -> str:
        observed_at = datetime.now(timezone.utc).isoformat()
        records = []
        for item in orderbooks:
            ticker = item.get("ticker")
            if isinstance(ticker, str):
                records.append((observed_at, ticker, json.dumps(item, ensure_ascii=False)))

        self.connection.executemany(
            "INSERT OR REPLACE INTO orderbook_snapshots (observed_at, ticker, payload) VALUES (?, ?, ?)",
            records,
        )
        self.connection.commit()
        return observed_at

    def close(self) -> None:
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        self.close()

