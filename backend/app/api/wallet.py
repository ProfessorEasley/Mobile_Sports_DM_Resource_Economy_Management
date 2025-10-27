from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..schemas import WalletAddRequest, WalletSpendRequest, WalletBalanceResponse, WalletUpdateRequest
from ..services.wallet_service import WalletService
from ..db.database import get_db
from ..auth import get_current_user
from ..models import Wallet

router = APIRouter(prefix="/wallet", tags=["wallet"])


class WalletDisplayResponse(BaseModel):
    player_id: str
    coins: float
    gems: float
    credits: float


@router.get("/display", response_model=WalletDisplayResponse)
def display_coins_gems(
    player_identifier: Optional[str] = Query(
        default=None,
        alias="player_id",
        description="Numeric player id or username whose wallet should be displayed. Defaults to the current player.",
    ),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    service = WalletService(db)
    resolved_player_id, response_identifier = service.resolve_player_identifier(player_identifier, user["user_id"])
    if resolved_player_id is None:
        raise HTTPException(status_code=404, detail="Player not found")
    balance = service.get_balance(resolved_player_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletDisplayResponse(
        player_id=response_identifier,
        coins=balance["coins"],
        gems=balance["gems"],
        credits=balance["credits"],
    )

@router.post("/add", response_model=WalletBalanceResponse)
def add_to_wallet(request: WalletAddRequest, user=Depends(get_current_user), db=Depends(get_db)):
    service = WalletService(db)
    success = service.add_currency(user["user_id"], request.currency_type, int(request.amount))
    if not success:
        raise HTTPException(status_code=400, detail="Add currency failed")
    balance = service.get_balance(user["user_id"])
    if not balance:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletBalanceResponse(**balance)

@router.post("/spend", response_model=WalletBalanceResponse)
def spend_from_wallet(request: WalletSpendRequest, user=Depends(get_current_user), db=Depends(get_db)):
    service = WalletService(db)
    success = service.spend_currency(user["user_id"], request.currency_type, int(request.amount))
    if not success:
        raise HTTPException(status_code=400, detail="Spend currency failed or insufficient balance")
    balance = service.get_balance(user["user_id"])
    return WalletBalanceResponse(**balance)

@router.get("/balance", response_model=WalletBalanceResponse)
def get_balance(currency_type: str = None, user=Depends(get_current_user), db=Depends(get_db)):
    service = WalletService(db)
    balance = service.get_balance(user["user_id"])
    if not balance:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletBalanceResponse(**balance)

@router.put("/update", response_model=WalletBalanceResponse)
def update_wallet(request: WalletUpdateRequest, user=Depends(get_current_user), db=Depends(get_db)):
    service = WalletService(db)
    wallet = db.query(Wallet).filter_by(user_id=user["user_id"]).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if request.coins is not None:
        wallet.coins = request.coins
    if request.gems is not None:
        wallet.gems = request.gems
    if request.credits is not None:
        wallet.credits = request.credits
    db.commit()
    balance = service.get_balance(user["user_id"])
    return WalletBalanceResponse(**balance)
