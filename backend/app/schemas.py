from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

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


class PerformanceMetricsRequest(BaseModel):
    leads_generated: int = 0
    conversion_rate: float = Field(0.0, ge=0.0, le=1.0)
    quality_score: float = Field(0.0, ge=0.0, le=100.0)
    team_performance: float = Field(0.0, ge=0.0, le=100.0)


class SalaryContractRequest(BaseModel):
    player_id: str
    base_salary: float = Field(..., gt=0.0)
    bonus_multiplier: float = Field(1.0, ge=0.0)
    performance_threshold: float = Field(0.75, ge=0.0, le=1.0)
    max_bonus_percentage: float = Field(0.5, ge=0.0, le=1.0)


class ContractDetailsResponse(BaseModel):
    player_id: str
    base_salary: float
    bonus_multiplier: float
    performance_threshold: float
    max_bonus_percentage: float


class SalaryCalculationBreakdown(BaseModel):
    base_salary: float
    performance_bonus: float
    total: float
    metrics_score: float


class SalaryActionResponse(BaseModel):
    player_id: str
    transaction_id: str
    currency: str
    new_balance: int
    status: str
    message: str
    salary_breakdown: Optional[SalaryCalculationBreakdown] = None


class BulkSalaryDeductionRequest(PerformanceMetricsRequest):
    player_id: str


class BulkSalaryDeductionResponse(BaseModel):
    results: Dict[str, bool]
    processed_count: int
    success_count: int