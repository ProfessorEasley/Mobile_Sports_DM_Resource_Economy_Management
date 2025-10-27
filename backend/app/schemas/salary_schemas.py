from pydantic import BaseModel
from typing import Optional, List, Dict
from decimal import Decimal

class PerformanceMetricsRequest(BaseModel):
    leads_generated: int = 0
    conversion_rate: float = 0.0  # 0.0 to 1.0
    quality_score: float = 0.0    # 0.0 to 100.0
    team_performance: float = 0.0 # 0.0 to 100.0

class SalaryContractRequest(BaseModel):
    base_salary: float
    bonus_multiplier: float = 1.0
    performance_threshold: float = 0.75
    max_bonus_percentage: float = 0.5

class PayoutCalculationResponse(BaseModel):
    base_salary: float
    performance_bonus: float
    total: float
    metrics_score: float

class ContractDetailsResponse(BaseModel):
    user_id: str
    base_salary: float
    bonus_multiplier: float
    performance_threshold: float
    max_bonus_percentage: float

class BulkPayoutRequest(BaseModel):
    user_id: str
    leads_generated: int = 0
    conversion_rate: float = 0.0
    quality_score: float = 0.0
    team_performance: float = 0.0

class BulkPayoutResponse(BaseModel):
    results: Dict[str, bool]
    processed_count: int
    success_count: int

class PayoutTriggerResponse(BaseModel):
    success: bool
    message: str
    payout_details: Optional[PayoutCalculationResponse] = None
