from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Literal, List


class TransactionResponse(BaseModel):
    id: UUID
    user_id: str
    amount: int
    currency: str
    type: Literal["earn", "spend"]
    timestamp: datetime
    source: str


class TransactionHistoryResponse(BaseModel):
    transactions: List[TransactionResponse]