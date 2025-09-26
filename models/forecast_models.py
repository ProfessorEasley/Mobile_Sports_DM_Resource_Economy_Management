from typing import Dict
from uuid import UUID

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    player_id: UUID
    current_balance: int
    weeks: int
    salary: int
    income: int
    expenses: Dict[str, int] = Field(default_factory=dict)
    bonuses: Dict[str, int] = Field(default_factory=dict)


class WeeklyForecast(BaseModel):
    week: int
    net_change: int
    balance: int


class EconomyForecastResponse(BaseModel):
    player_id: UUID
    current_balance: int
    weeks: int
    salary: int
    income: int
    bonuses: Dict[str, int]
    expenses: Dict[str, int]
    forecast: list[WeeklyForecast]
    alerts: list[str] = Field(default_factory=list)
