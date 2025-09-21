from typing import List

from models.forecast_models import ForecastEntry


def to_response_model(data: list[dict]) -> List[ForecastEntry]:
    return [ForecastEntry(**item) for item in data]
