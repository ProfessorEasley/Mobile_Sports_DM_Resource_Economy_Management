from pydantic import BaseModel
from typing import Optional

class WalletAddRequest(BaseModel):
    currency_type: str
    amount: float

class WalletSpendRequest(BaseModel):
    currency_type: str
    amount: float

class WalletBalanceResponse(BaseModel):
    coins: float
    gems: float
    credits: float

class CurrencyAddRequest(BaseModel):
    amount: float

class CurrencySpendRequest(BaseModel):
    amount: float

class CurrencyBalanceResponse(BaseModel):
    balance: float

class WalletUpdateRequest(BaseModel):
    coins: Optional[int]
    gems: Optional[int]
    credits: Optional[int]
