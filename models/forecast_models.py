from pydantic import BaseModel
from typing import Dict

class ForecastRequest(BaseModel):
    current_balance: int
    weeks: int
    salary: int
    income: int
    expenses: Dict[str, int] = {}
    bonuses: Dict[str, int] = {}

class ForecastResponse(BaseModel):
    week: int
    income: int
    salary: int
    bonus: int
    expenses: int
    net_change: int
    balance: int
