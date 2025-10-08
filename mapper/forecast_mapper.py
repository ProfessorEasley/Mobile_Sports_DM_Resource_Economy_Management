from models.forecast_models import WeeklyForecast

def to_response_model(data: list[dict]) -> list[WeeklyForecast]:
    return [WeeklyForecast(**item) for item in data]
