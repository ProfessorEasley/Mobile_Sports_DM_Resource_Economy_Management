from models.forecast_models import EconomyForecast, ForecastRequest, Response
from processors.alert_rules import evaluate_behavior_risks
from processors.forecast_processor import compute_forecast
from mapper.forecast_mapper import to_response_model

def run_forecast(request: ForecastRequest) -> Response:
    raw = compute_forecast(request)
    response = to_response_model(raw)
    alerts = evaluate_behavior_risks(raw)

    economy_forecasting = EconomyForecast(
        player_id=request.player_id,
        current_balance=request.current_balance,
        weeks=request.weeks,
        salary=request.salary,
        income=request.income,
        bonuses=request.bonuses,
        expenses=request.expenses,
        forecast=response,
        alerts=alerts,
    )

    return Response(economy_forecasting=economy_forecasting)
