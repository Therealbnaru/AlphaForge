from probability_model import LogisticModel


def make_probability_strategy(model: LogisticModel, minimum_edge: float, quantity: float = 1.0):
    bought_tickers = set()

    def strategy(row: dict) -> dict:
        ticker = row.get("ticker")
        ask = row.get("ask")
        probability = model.predict_probability(row)

        if ticker in bought_tickers:
            return {"action": "hold", "quantity": 0}
        if not isinstance(ticker, str) or not isinstance(ask, (int, float)):
            return {"action": "hold", "quantity": 0}
        if probability is None:
            return {"action": "hold", "quantity": 0}

        edge = probability - ask
        if edge < minimum_edge:
            return {"action": "hold", "quantity": 0}

        bought_tickers.add(ticker)
        return {"action": "buy", "quantity": quantity, "edge": edge}

    return strategy

