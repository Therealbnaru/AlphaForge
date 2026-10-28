import math


def evaluate_calibration(rows: list[dict], bin_count: int = 10) -> dict:
    if bin_count <= 0:
        raise ValueError("bin_count must be positive")

    valid_rows = []
    for row in rows:
        probability = row.get("probability")
        outcome = row.get("outcome")

        if not isinstance(probability, (int, float)):
            continue
        if probability < 0 or probability > 1:
            continue
        if outcome not in (0, 1):
            continue

        valid_rows.append({"probability": float(probability), "outcome": outcome})

    if not valid_rows:
        return {"count": 0, "brier_score": None, "log_loss": None, "bins": []}

    brier_total = 0.0
    log_loss_total = 0.0
    bins = []

    for bin_number in range(bin_count):
        lower_bound = bin_number / bin_count
        upper_bound = (bin_number + 1) / bin_count
        bin_rows = []

        for row in valid_rows:
            probability = row["probability"]
            is_last_bin = bin_number == bin_count - 1
            in_bin = lower_bound <= probability < upper_bound
            if is_last_bin:
                in_bin = lower_bound <= probability <= upper_bound
            if in_bin:
                bin_rows.append(row)

        if bin_rows:
            average_prediction = sum(row["probability"] for row in bin_rows) / len(bin_rows)
            observed_rate = sum(row["outcome"] for row in bin_rows) / len(bin_rows)
            calibration_error = abs(average_prediction - observed_rate)
        else:
            average_prediction = None
            observed_rate = None
            calibration_error = None

        bins.append({
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "count": len(bin_rows),
            "average_prediction": average_prediction,
            "observed_rate": observed_rate,
            "calibration_error": calibration_error,
        })

    for row in valid_rows:
        probability = min(max(row["probability"], 0.000001), 0.999999)
        outcome = row["outcome"]
        brier_total += (probability - outcome) ** 2
        log_loss_total -= outcome * math.log(probability)
        log_loss_total -= (1 - outcome) * math.log(1 - probability)

    count = len(valid_rows)
    return {
        "count": count,
        "brier_score": brier_total / count,
        "log_loss": log_loss_total / count,
        "bins": bins,
    }

