import argparse

from collector import run_collector


def main():
    parser = argparse.ArgumentParser(description="Collect read-only Kalshi market data for AlphaForge.")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--iterations", type=int, default=None)
    parser.add_argument("--microstructure-count", type=int, default=10)
    parser.add_argument("--trade-limit", type=int, default=100)
    parser.add_argument("--market-limit", type=int, default=None)
    parser.add_argument("--directory", default="data")
    arguments = parser.parse_args()

    run_collector(
        interval_seconds=arguments.interval,
        iterations=arguments.iterations,
        directory=arguments.directory,
        microstructure_count=arguments.microstructure_count,
        trade_limit=arguments.trade_limit,
        market_limit=arguments.market_limit,
    )


if __name__ == "__main__":
    main()

