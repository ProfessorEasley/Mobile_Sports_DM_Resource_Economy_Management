from fastapi import APIRouter, Depends
from ..schemas import CurrencyAddRequest, CurrencySpendRequest, CurrencyBalanceResponse
from ..services.wallet_service import add_coins, spend_coins, get_coins_balance
from ..auth import get_current_user

router = APIRouter(prefix="/coins", tags=["coins"])

@router.post("/add", response_model=CurrencyBalanceResponse)
def add(request: CurrencyAddRequest, user=Depends(get_current_user)):
    return add_coins(user, request)

@router.post("/spend", response_model=CurrencyBalanceResponse)
def spend(request: CurrencySpendRequest, user=Depends(get_current_user)):
    return spend_coins(user, request)

@router.get("/balance", response_model=CurrencyBalanceResponse)
def balance(user=Depends(get_current_user)):
    return get_coins_balance(user)
