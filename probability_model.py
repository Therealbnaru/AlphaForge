import math
from dataclasses import dataclass


@dataclass
class LogisticModel:
    feature_names: list[str]
    weights: list[float]
    bias: float
    means: list[float]
    scales: list[float]

    def predict_probability(self, row: dict) -> float | None:
        values = []
        for feature_name in self.feature_names:
            value = row.get(feature_name)
            if not isinstance(value, (int, float)):
                return None
            values.append(float(value))

        score = self.bias
        for index, value in enumerate(values):
            normalized_value = (value - self.means[index]) / self.scales[index]
            score += self.weights[index] * normalized_value

        score = max(-60.0, min(60.0, score))
        return 1 / (1 + math.exp(-score))


def _training_rows(rows: list[dict], feature_names: list[str]) -> list[dict]:
    valid_rows = []

    for row in rows:
        outcome = row.get("outcome")
        if outcome not in (0, 1):
            continue

        has_all_features = True
        for feature_name in feature_names:
            if not isinstance(row.get(feature_name), (int, float)):
                has_all_features = False
                break

        if has_all_features:
            valid_rows.append(row)

    return valid_rows


def fit_logistic_model(rows: list[dict], feature_names: list[str], learning_rate: float = 0.1, epochs: int = 500) -> LogisticModel:
    if not feature_names:
        raise ValueError("feature_names cannot be empty")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be positive")
    if epochs <= 0:
        raise ValueError("epochs must be positive")

    valid_rows = _training_rows(rows, feature_names)
    if not valid_rows:
        raise ValueError("no rows contain a complete feature set and valid outcome")

    means = []
    scales = []
    for feature_name in feature_names:
        values = [float(row[feature_name]) for row in valid_rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        scale = variance ** 0.5
        if scale == 0:
            scale = 1.0
        means.append(mean)
        scales.append(scale)

    weights = [0.0 for feature_name in feature_names]
    bias = 0.0

    for epoch in range(epochs):
        weight_gradients = [0.0 for feature_name in feature_names]
        bias_gradient = 0.0

        for row in valid_rows:
            normalized_values = []
            for index, feature_name in enumerate(feature_names):
                value = float(row[feature_name])
                normalized_value = (value - means[index]) / scales[index]
                normalized_values.append(normalized_value)

            score = bias
            for index, normalized_value in enumerate(normalized_values):
                score += weights[index] * normalized_value

            score = max(-60.0, min(60.0, score))
            probability = 1 / (1 + math.exp(-score))
            error = probability - row["outcome"]
            bias_gradient += error

            for index, normalized_value in enumerate(normalized_values):
                weight_gradients[index] += error * normalized_value

        row_count = len(valid_rows)
        bias -= learning_rate * bias_gradient / row_count
        for index in range(len(weights)):
            weights[index] -= learning_rate * weight_gradients[index] / row_count

    return LogisticModel(feature_names, weights, bias, means, scales)

