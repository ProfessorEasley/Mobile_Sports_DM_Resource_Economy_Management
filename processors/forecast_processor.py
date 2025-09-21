def _lookup_week_value(payload: dict, week: int) -> int:
    """Support both numeric and prefixed week keys in the request payload."""

    if not payload:
        return 0

    keys = (str(week), f"week_{week}", week)
    for key in keys:
        if key in payload:
            return payload[key]
    return 0


def compute_forecast(request):
    balance = request.current_balance
    output = []
    for week in range(1, request.weeks + 1):
        bonus = _lookup_week_value(request.bonuses, week)
        expense = _lookup_week_value(request.expenses, week)
        net = request.income - request.salary + bonus - expense
        balance += net
        output.append({
            "week": week,
            "balance": balance,
            "net_change": net,
            "income": request.income,
            "salary": request.salary,
            "bonus": bonus,
            "expenses": expense,
        })
    return output
