from pydantic import BaseModel
from typing import Optional

class WalletDisplayResponse(BaseModel):
    player_id: str
    coins: float
    gems: float
    credits: float

class WalletUpdateRequest(BaseModel):
    player_id: str
    currency: str           
    amount: int
    operation: str          
    source: Optional[str] = None

class WalletActionResponse(BaseModel):
    player_id: str
    transaction_id: str
    currency: str
    new_balance: int
    status: str
    message: str