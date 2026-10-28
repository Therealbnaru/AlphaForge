from calibration import evaluate_calibration
from probability_model import LogisticModel, fit_logistic_model


def _model_rows(model: LogisticModel, rows: list[dict]) -> list[dict]:
    predictions = []

    for row in rows:
        outcome = row.get("outcome")
        probability = model.predict_probability(row)

        if outcome not in (0, 1) or probability is None:
            continue

        predictions.append({
            "probability": probability,
            "outcome": outcome,
        })

    return predictions


def run_probability_experiment(rows: list[dict], feature_names: list[str], learning_rate: float = 0.1, epochs: int = 500) -> dict:
    train_end = int(len(rows) * 0.6)
    validation_end = int(len(rows) * 0.8)
    if train_end <= 0 or validation_end <= train_end or validation_end >= len(rows):
        raise ValueError("rows must contain enough data for train, validation, and test periods")

    train_rows = rows[:train_end]
    validation_rows = rows[train_end:validation_end]
    test_rows = rows[validation_end:]
    model = fit_logistic_model(train_rows, feature_names, learning_rate, epochs)

    train_report = evaluate_calibration(_model_rows(model, train_rows))
    validation_report = evaluate_calibration(_model_rows(model, validation_rows))
    test_report = evaluate_calibration(_model_rows(model, test_rows))

    return {
        "feature_names": feature_names,
        "train": train_report,
        "validation": validation_report,
        "test": test_report,
    }

