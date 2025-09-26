from fastapi import APIRouter
from models.forecast_models import EconomyForecastResponse, ForecastRequest
from service.economy_service import run_forecast

router = APIRouter()

@router.post("/forecast", response_model=EconomyForecastResponse)
def forecast(data: ForecastRequest):
    return run_forecast(data)
