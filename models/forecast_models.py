from uuid import UUID
from typing import Dict, List

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    """Incoming payload for forecasting requests."""

    player_id: UUID
    current_balance: int
    weeks: int
    salary: int
    income: int
    bonuses: Dict[str, int] = Field(default_factory=dict)
    expenses: Dict[str, int] = Field(default_factory=dict)


class ForecastEntry(BaseModel):
    """Single week snapshot for the forecast response."""

    week: int
    balance: int
    net_change: int
    income: int
    salary: int
    bonus: int
    expenses: int


class EconomyForecast(BaseModel):
    """Top-level economy forecasting response section."""

    player_id: UUID
    current_balance: int
    weeks: int
    salary: int
    income: int
    bonuses: Dict[str, int]
    expenses: Dict[str, int]
    forecast: List[ForecastEntry]
    alerts: List[str] = Field(default_factory=list)


class Response(BaseModel):
    """Canonical response envelope returned by the forecast API."""

    economy_forecasting: EconomyForecast
