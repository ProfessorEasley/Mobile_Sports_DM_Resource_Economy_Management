from models.forecast_models import ForecastResponse

def to_response_model(data: list[dict]) -> list[ForecastResponse]:
    return [ForecastResponse(**item) for item in data]
