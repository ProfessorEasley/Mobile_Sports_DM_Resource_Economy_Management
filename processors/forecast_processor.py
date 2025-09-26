def compute_forecast(request):
    balance = request.current_balance
    output = []
    for week in range(1, request.weeks + 1):
        bonus = request.bonuses.get(str(week), 0)
        expense = request.expenses.get(str(week), 0)
        net = request.income - request.salary + bonus - expense
        balance += net
        output.append({
            "week": week,
            "net_change": net,
            "balance": balance
        })
    return output
