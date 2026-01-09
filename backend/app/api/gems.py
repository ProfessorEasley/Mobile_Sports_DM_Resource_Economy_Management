from fastapi import APIRouter, Depends
from ..schemas import CurrencyAddRequest, CurrencySpendRequest, CurrencyBalanceResponse
from ..services.wallet_service import add_gems, spend_gems, get_gems_balance
from ..auth import get_current_user

router = APIRouter(prefix="/gems", tags=["gems"])

@router.post("/add", response_model=CurrencyBalanceResponse)
def add(request: CurrencyAddRequest, user=Depends(get_current_user)):
    return add_gems(user, request)

@router.post("/spend", response_model=CurrencyBalanceResponse)
def spend(request: CurrencySpendRequest, user=Depends(get_current_user)):
    return spend_gems(user, request)

@router.get("/balance", response_model=CurrencyBalanceResponse)
def balance(user=Depends(get_current_user)):
    return get_gems_balance(user)
