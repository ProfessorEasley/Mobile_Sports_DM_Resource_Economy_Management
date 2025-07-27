from fastapi import APIRouter
from models.forecast_models import ForecastRequest, ForecastResponse, Response
from service.economy_service import run_forecast

router = APIRouter()

@router.post("/forecast", response_model=Response)
def forecast(data: ForecastRequest):
    return run_forecast(data)
