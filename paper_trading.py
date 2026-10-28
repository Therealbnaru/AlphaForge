from dataclasses import dataclass, field


@dataclass
class Position:
    quantity: float = 0.0
    average_price: float = 0.0


@dataclass
class RiskLimits:
    max_position_quantity: float | None = None
    max_order_cost: float | None = None


@dataclass
class PaperPortfolio:
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)
    realized_profit: float = 0.0
    risk_limits: RiskLimits | None = None
    fee_per_contract: float = 0.0

    def buy(self, ticker: str, quantity: float, price: float) -> None:
        self._check_order(quantity, price)

        cost = quantity * price + quantity * self.fee_per_contract
        if cost > self.cash:
            raise ValueError("not enough paper cash")

        position = self.positions.get(ticker, Position())
        if self.risk_limits is not None:
            if self.risk_limits.max_order_cost is not None and cost > self.risk_limits.max_order_cost:
                raise ValueError("order cost exceeds paper risk limit")
            if self.risk_limits.max_position_quantity is not None:
                if position.quantity + quantity > self.risk_limits.max_position_quantity:
                    raise ValueError("position size exceeds paper risk limit")

        old_value = position.quantity * position.average_price
        new_quantity = position.quantity + quantity
        new_value = old_value + cost

        position.quantity = new_quantity
        position.average_price = new_value / new_quantity
        self.positions[ticker] = position
        self.cash -= cost

    def sell(self, ticker: str, quantity: float, price: float) -> None:
        self._check_order(quantity, price)

        position = self.positions.get(ticker)
        if position is None or quantity > position.quantity:
            raise ValueError("not enough paper position")

        proceeds = quantity * price - quantity * self.fee_per_contract
        cost = quantity * position.average_price
        self.realized_profit += proceeds - cost
        position.quantity -= quantity
        self.cash += proceeds

        if position.quantity == 0:
            del self.positions[ticker]

    def equity(self, prices: dict[str, float]) -> float:
        total_value = self.cash

        for ticker, position in self.positions.items():
            if ticker in prices:
                total_value += position.quantity * prices[ticker]

        return total_value

    def _check_order(self, quantity: float, price: float) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        if price < 0 or price > 1:
            raise ValueError("price must be between 0 and 1")

