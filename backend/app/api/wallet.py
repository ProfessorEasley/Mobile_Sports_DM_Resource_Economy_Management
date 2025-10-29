from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..schemas import WalletDisplayResponse, WalletUpdateRequest, WalletActionResponse
from ..services.wallet_service import WalletService
from ..db.database import get_db
from ..auth import get_current_user
from ..models import Wallet

router = APIRouter(prefix="/wallet", tags=["wallet"])


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

@router.post("/update", response_model=WalletActionResponse)
def update_wallet(request: WalletUpdateRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if request.currency not in {"coins", "gems", "credits"}:
        raise HTTPException(status_code=400, detail="invalid currency")
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    if request.operation not in {"earn", "spend"}:
        raise HTTPException(status_code=400, detail="invalid operation")

    service = WalletService(db)

    resolved_player_id, response_identifier = service.resolve_player_identifier(request.player_id, user["user_id"])
    if resolved_player_id is None:
        raise HTTPException(status_code=404, detail="player not found")

    if request.operation == "earn":
        ok = service.add_currency(resolved_player_id, request.currency, int(request.amount))
        verb = "earned"
    else:
        ok = service.spend_currency(resolved_player_id, request.currency, int(request.amount))
        verb = "spent"

    if not ok:
        raise HTTPException(status_code=400, detail="wallet update failed")

    balance = service.get_balance(resolved_player_id)
    if not balance:
        raise HTTPException(status_code=404, detail="wallet not found")

    return {
        "player_id": response_identifier,
        "transaction_id": str(uuid4()),
        "currency": request.currency,
        "new_balance": int(balance[request.currency]),
        "status": "success",
        "message": f"{request.amount} {request.currency} {verb}" + (f" on {request.source}" if request.source else "")
    }