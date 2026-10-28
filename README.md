# AlphaForge

AlphaForge is a paper-trading quantitative research engine for Kalshi prediction markets.

The project currently provides:

- Read-only market, trade, and order-book collection.
- JSON and SQLite historical storage.
- Market and order-book feature generation.
- Calibration and factor-discovery experiments.
- Logistic probability modeling.
- Paper portfolio accounting.
- Backtesting with settlement, fees, slippage, position limits, and drawdown controls.

Live order submission is not implemented.

## Setup

Use the project virtual environment:

```powershell
c:/Users/bhuva/Desktop/AlphaForge/.venv/Scripts/python.exe
```

## Collect data

Run a bounded test collection:

```powershell
c:/Users/bhuva/Desktop/AlphaForge/.venv/Scripts/python.exe collect_data.py --iterations 1 --market-limit 100 --microstructure-count 10 --trade-limit 100
```

Run continuous collection:

```powershell
c:/Users/bhuva/Desktop/AlphaForge/.venv/Scripts/python.exe collect_data.py --interval 60 --microstructure-count 10 --trade-limit 100
```

Collected data is written to the local `data/` directory, which is intentionally excluded from Git.

## Research commands

```powershell
c:/Users/bhuva/Desktop/AlphaForge/.venv/Scripts/python.exe data_quality.py
c:/Users/bhuva/Desktop/AlphaForge/.venv/Scripts/python.exe run_calibration.py
c:/Users/bhuva/Desktop/AlphaForge/.venv/Scripts/python.exe run_factor_discovery.py
c:/Users/bhuva/Desktop/AlphaForge/.venv/Scripts/python.exe run_probability_experiment.py
c:/Users/bhuva/Desktop/AlphaForge/.venv/Scripts/python.exe run_model_backtest.py
```

