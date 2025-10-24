from fastapi import APIRouter, Query
from typing import Optional
from models.forecast_models import EconomyForecastResponse, ForecastRequest
from models.transactions_models import TransactionResponse
from service.economy_service import run_forecast
from service.transaction_service import get_transaction_history

router = APIRouter()

@router.post("/forecast", response_model=EconomyForecastResponse)
def forecast(data: ForecastRequest):
    return run_forecast(data)

@router.get("/wallet/transactions", response_model=list[TransactionResponse])
def get_transactions(
    user_id: str = Query(..., description="User identifier"),
    limit: Optional[int] = Query(5, description="Maximum number of transactions to return")
):
 
    return get_transaction_history(user_id, limit)
