from models.forecast_models import ForecastRequest
from processors.alert_rules import evaluate_behavior_risks
from processors.forecast_processor import compute_forecast
from mapper.forecast_mapper import to_response_model

def run_forecast(request: ForecastRequest):
    raw = compute_forecast(request)
    response = to_response_model(raw)
    alerts = evaluate_behavior_risks(raw)
    return {"forecast": response, "alerts": alerts}
