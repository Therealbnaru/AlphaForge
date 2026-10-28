from collections.abc import Callable


def _correlation(rows: list[dict], factor: Callable[[dict], object]) -> tuple[float | None, int]:
    values = []
    outcomes = []

    for row in rows:
        value = factor(row)
        outcome = row.get("outcome")

        if not isinstance(value, (int, float)):
            continue
        if not isinstance(outcome, (int, float)):
            continue

        values.append(float(value))
        outcomes.append(float(outcome))

    if len(values) < 2:
        return None, len(values)

    value_average = sum(values) / len(values)
    outcome_average = sum(outcomes) / len(outcomes)
    numerator = 0.0
    value_variance = 0.0
    outcome_variance = 0.0

    for value, outcome in zip(values, outcomes):
        value_difference = value - value_average
        outcome_difference = outcome - outcome_average
        numerator += value_difference * outcome_difference
        value_variance += value_difference ** 2
        outcome_variance += outcome_difference ** 2

    denominator = (value_variance * outcome_variance) ** 0.5
    if denominator == 0:
        return None, len(values)

    return numerator / denominator, len(values)


def _get_mid(row: dict) -> object:
    return row.get("probability")


def _get_one_minus_mid(row: dict) -> object:
    probability = row.get("probability")
    if isinstance(probability, (int, float)):
        return 1 - probability
    return None


def _get_spread(row: dict) -> object:
    return row.get("spread")


def _get_volume(row: dict) -> object:
    return row.get("volume")


def _get_volume_24h(row: dict) -> object:
    return row.get("volume_24h")


def _get_liquidity(row: dict) -> object:
    return row.get("liquidity")


def _get_hours_until_expiration(row: dict) -> object:
    return row.get("hours_until_expiration")


def _factor_definitions() -> list[tuple[str, Callable[[dict], object]]]:
    return [
        ("mid", _get_mid),
        ("one_minus_mid", _get_one_minus_mid),
        ("spread", _get_spread),
        ("volume", _get_volume),
        ("volume_24h", _get_volume_24h),
        ("liquidity", _get_liquidity),
        ("hours_until_expiration", _get_hours_until_expiration),
    ]


def discover_factors(rows: list[dict], train_fraction: float = 0.7) -> list[dict]:
    if not rows:
        return []
    if train_fraction <= 0 or train_fraction >= 1:
        raise ValueError("train_fraction must be between 0 and 1")

    split_index = int(len(rows) * train_fraction)
    if split_index <= 0 or split_index >= len(rows):
        raise ValueError("rows must contain enough data for train and test periods")

    train_rows = rows[:split_index]
    test_rows = rows[split_index:]
    discoveries = []

    for name, factor in _factor_definitions():
        train_correlation, train_count = _correlation(train_rows, factor)
        test_correlation, test_count = _correlation(test_rows, factor)

        discoveries.append({
            "name": name,
            "train_correlation": train_correlation,
            "test_correlation": test_correlation,
            "train_count": train_count,
            "test_count": test_count,
        })

    discoveries.sort(
        key=lambda discovery: abs(discovery["test_correlation"] or 0),
        reverse=True,
    )
    return discoveries

