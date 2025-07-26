from fastapi import APIRouter
from models.forecast_models import ForecastRequest, ForecastResponse
from service.economy_service import run_forecast

router = APIRouter()

@router.post("/forecast", response_model=list[ForecastResponse])
def forecast(data: ForecastRequest):
    return run_forecast(data)
