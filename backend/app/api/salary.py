from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from decimal import Decimal

# Local schemas for salary API
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
    results: dict
    processed_count: int
    success_count: int

class PayoutTriggerResponse(BaseModel):
    success: bool
    message: str
    payout_details: PayoutCalculationResponse = None
from ..services.salary_engine import LeadSalaryEngine, PerformanceMetrics, SalaryContract
from ..db.database import get_db
from ..auth import get_current_user
from decimal import Decimal

router = APIRouter(prefix="/salary", tags=["salary"])

@router.post("/contract/register")
def register_salary_contract(
    contract_data: SalaryContractRequest, 
    user=Depends(get_current_user), 
    db=Depends(get_db)
):
    """Register a new salary contract for the current user"""
    engine = LeadSalaryEngine(db)
    
    contract = SalaryContract(
        user_id=user["user_id"],
        base_salary=Decimal(str(contract_data.base_salary)),
        bonus_multiplier=contract_data.bonus_multiplier,
        performance_threshold=contract_data.performance_threshold,
        max_bonus_percentage=contract_data.max_bonus_percentage
    )
    
    engine.register_contract(contract)
    
    return {
        "message": f"Salary contract registered for user {user['user_id']}",
        "contract": {
            "base_salary": contract_data.base_salary,
            "bonus_multiplier": contract_data.bonus_multiplier,
            "performance_threshold": contract_data.performance_threshold,
            "max_bonus_percentage": contract_data.max_bonus_percentage
        }
    }

@router.get("/contract/details", response_model=ContractDetailsResponse)
def get_contract_details(user=Depends(get_current_user), db=Depends(get_db)):
    """Get salary contract details for the current user"""
    engine = LeadSalaryEngine(db)
    contract_details = engine.get_contract_details(user["user_id"])
    
    if not contract_details:
        raise HTTPException(status_code=404, detail="No salary contract found for user")
    
    return ContractDetailsResponse(**contract_details)

@router.post("/calculate/weekly", response_model=PayoutCalculationResponse)
def calculate_weekly_payout(
    metrics: PerformanceMetricsRequest, 
    user=Depends(get_current_user), 
    db=Depends(get_db)
):
    """Calculate weekly payout based on performance metrics"""
    engine = LeadSalaryEngine(db)
    
    performance_metrics = PerformanceMetrics(
        leads_generated=metrics.leads_generated,
        conversion_rate=metrics.conversion_rate,
        quality_score=metrics.quality_score,
        team_performance=metrics.team_performance
    )
    
    payout_details = engine.calculate_weekly_payout(user["user_id"], performance_metrics)
    
    return PayoutCalculationResponse(
        base_salary=float(payout_details["base_salary"]),
        performance_bonus=float(payout_details["performance_bonus"]),
        total=float(payout_details["total"]),
        metrics_score=float(payout_details["metrics_score"])
    )

@router.post("/trigger/weekly", response_model=PayoutTriggerResponse)
def trigger_weekly_payout(
    metrics: PerformanceMetricsRequest, 
    user=Depends(get_current_user), 
    db=Depends(get_db)
):
    """Trigger weekly payout and update wallet (external contract trigger simulation)"""
    engine = LeadSalaryEngine(db)
    
    performance_metrics = PerformanceMetrics(
        leads_generated=metrics.leads_generated,
        conversion_rate=metrics.conversion_rate,
        quality_score=metrics.quality_score,
        team_performance=metrics.team_performance
    )
    
    # Calculate payout details first
    payout_details = engine.calculate_weekly_payout(user["user_id"], performance_metrics)
    
    # Trigger the actual payout
    success = engine.trigger_weekly_payout(user["user_id"], performance_metrics)
    
    if success:
        return PayoutTriggerResponse(
            success=True,
            message="Weekly payout processed successfully",
            payout_details=PayoutCalculationResponse(
                base_salary=float(payout_details["base_salary"]),
                performance_bonus=float(payout_details["performance_bonus"]),
                total=float(payout_details["total"]),
                metrics_score=float(payout_details["metrics_score"])
            )
        )
    else:
        return PayoutTriggerResponse(
            success=False,
            message="Failed to process weekly payout"
        )

@router.post("/trigger/bulk", response_model=BulkPayoutResponse)
def trigger_bulk_payouts(
    payout_requests: List[BulkPayoutRequest], 
    user=Depends(get_current_user), 
    db=Depends(get_db)
):
    """Trigger bulk payouts for multiple users (admin/external contract trigger)"""
    engine = LeadSalaryEngine(db)
    
    # Convert requests to the format expected by the engine
    payout_data = []
    for request in payout_requests:
        payout_data.append({
            "user_id": request.user_id,
            "leads_generated": request.leads_generated,
            "conversion_rate": request.conversion_rate,
            "quality_score": request.quality_score,
            "team_performance": request.team_performance
        })
    
    results = engine.process_bulk_payouts(payout_data)
    success_count = sum(1 for success in results.values() if success)
    
    return BulkPayoutResponse(
        results=results,
        processed_count=len(results),
        success_count=success_count
    )

@router.get("/performance/bonus/{amount}")
def calculate_performance_bonus(
    amount: int,
    metrics: PerformanceMetricsRequest, 
    user=Depends(get_current_user), 
    db=Depends(get_db)
):
    """Calculate performance bonus for given metrics"""
    engine = LeadSalaryEngine(db)
    
    performance_metrics = PerformanceMetrics(
        leads_generated=metrics.leads_generated,
        conversion_rate=metrics.conversion_rate,
        quality_score=metrics.quality_score,
        team_performance=metrics.team_performance
    )
    
    bonus = engine.calculate_performance_bonus(user["user_id"], performance_metrics)
    
    return {
        "user_id": user["user_id"],
        "performance_bonus": float(bonus),
        "metrics": {
            "leads_generated": metrics.leads_generated,
            "conversion_rate": metrics.conversion_rate,
            "quality_score": metrics.quality_score,
            "team_performance": metrics.team_performance
        }
    }
