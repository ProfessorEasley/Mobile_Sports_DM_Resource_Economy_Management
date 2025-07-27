def evaluate_behavior_risks(forecast: list[dict]) -> list[str]:
    alerts = []
    for week in forecast:
        w = week["week"]
        if week["balance"] < 50:
            alerts.append(f"Week {w}: Balance dropped below 50")
        if week["net_change"] < 0 and abs(week["net_change"]) > 50:
            alerts.append(f"Week {w}: High overspending detected")
    return alerts
