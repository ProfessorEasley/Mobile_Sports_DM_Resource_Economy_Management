"""
WalletService: Core wallet logic for add, spend, get operations with transactional safety.
"""
from typing import Optional, Dict, Tuple
from sqlalchemy.orm import Session

from ..models import User, Wallet, AuditLog

VALID_CURRENCIES = {"coins", "gems", "credits"}


class WalletService:
    def __init__(self, db: Session):
        self.db = db

    def resolve_player_identifier(self, identifier: Optional[str], fallback_user_id: int) -> Tuple[Optional[int], Optional[str]]:
        """
        Resolve player-supplied identifier to an internal numeric id. Allows numeric ids (e.g. "4").
        Returns a tuple of (resolved_player_id, display_identifier) where the second value is echoed back in API responses.
        """
        if identifier is None:
            player = self.db.query(User).filter_by(id=fallback_user_id).first()
            if not player:
                return None, None
            return player.id, str(player.id)

        lookup = identifier.strip()
        if not lookup:
            return None, None

        if lookup.isdigit():
            player = self.db.query(User).filter_by(id=int(lookup)).first()
            if player:
                return player.id, str(player.id)
            return None, None

        player = self.db.query(User).filter_by(username=lookup).first()
        if player:
            return player.id, player.username
        return None, None

    def get_balance(self, user_id: int) -> Optional[Dict[str, int]]:
        wallet = self.db.query(Wallet).filter_by(user_id=user_id).first()
        if wallet:
            return {
                "coins": wallet.coins,
                "gems": wallet.gems,
                "credits": wallet.credits,
            }
        return None

    def add_currency(self, user_id: int, currency_type: str, amount: int) -> bool:
        if currency_type not in VALID_CURRENCIES or amount < 1:
            return False

        wallet = self.db.query(Wallet).filter_by(user_id=user_id).first()

        if not wallet:
            wallet = Wallet(user_id=user_id, coins=0, gems=0, credits=0)
            self.db.add(wallet)
            self.db.flush() 

        current_value = getattr(wallet, currency_type, 0)
        setattr(wallet, currency_type, current_value + amount)

        self.db.add(
            AuditLog(
                user_id=user_id,
                wallet_id=wallet.id,
                currency_type=currency_type,
                operation="add",
                amount=amount,
                balance_after=getattr(wallet, currency_type),
                meta=None,
            )
        )
        self.db.commit() 
        return True


    def spend_currency(self, user_id: int, currency_type: str, amount: int) -> bool:
        if currency_type not in VALID_CURRENCIES or amount < 1:
            return False

        wallet = self.db.query(Wallet).filter_by(user_id=user_id).first()
        if not wallet:
            return False

        current_balance = getattr(wallet, currency_type, None)
        if current_balance is None or current_balance < amount:
            return False

        setattr(wallet, currency_type, current_balance - amount)

        self.db.add(
            AuditLog(
                user_id=user_id,
                wallet_id=wallet.id,
                currency_type=currency_type,
                operation="spend",
                amount=amount,
                balance_after=getattr(wallet, currency_type),
                meta=None,
            )
        )
        self.db.commit()  
        return True
