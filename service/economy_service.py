from models.forecast_models import ForecastRequest
from processors.forecast_processor import compute_forecast
from mapper.forecast_mapper import to_response_model

def run_forecast(request: ForecastRequest):
    raw_result = compute_forecast(request)
    return to_response_model(raw_result)
