from __future__ import annotations

from decimal import Decimal
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from ..auth import get_current_user
from ..db.database import get_db
from ..services.salary_engine import SalaryEngine, PerformanceMetrics, SalaryContract

from ..schemas import (
    PerformanceMetricsRequest,
    SalaryContractRequest,
    ContractDetailsResponse,
    SalaryCalculationBreakdown,
    SalaryActionResponse,
    BulkSalaryDeductionRequest,
    BulkSalaryDeductionResponse,
)

router = APIRouter(prefix="/salary", tags=["salary"])


@router.post("/contract/register", response_model=SalaryActionResponse)
def register_salary_contract(
    request: SalaryContractRequest,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    # This stores the contract in-memory inside SalaryEngine.
    engine = SalaryEngine(db)

    ok = engine.register_contract(
        SalaryContract(
            player_id=request.player_id,
            base_salary=Decimal(str(request.base_salary)),
            bonus_multiplier=request.bonus_multiplier,
            performance_threshold=request.performance_threshold,
            max_bonus_percentage=request.max_bonus_percentage,
        )
    )

    if not ok:
        raise HTTPException(status_code=400, detail="salary contract registration failed")

    return SalaryActionResponse(
        player_id=request.player_id,
        transaction_id=str(uuid4()),
        currency="coins",
        new_balance=0,
        status="success",
        message="Salary contract registered successfully",
        salary_breakdown=None,
    )


@router.get("/contract/details", response_model=ContractDetailsResponse)
def get_contract_details(
    player_id: str,
    db=Depends(get_db),
):
    engine = SalaryEngine(db)
    details = engine.get_contract_details(player_id)
    if not details:
        raise HTTPException(status_code=404, detail="salary contract not found")
    return ContractDetailsResponse(**details)


@router.post("/calculate/weekly", response_model=SalaryActionResponse)
def calculate_weekly_salary_cost(
    player_id: str,
    metrics: PerformanceMetricsRequest,
    user=Depends(get_current_user),
    db=Depends(get_db),
):

    engine = SalaryEngine(db)
    perf = PerformanceMetrics(
        leads_generated=metrics.leads_generated,
        conversion_rate=metrics.conversion_rate,
        quality_score=metrics.quality_score,
        team_performance=metrics.team_performance,
    )

    details = engine.calculate_weekly_salary_cost(player_id, perf)

    return SalaryActionResponse(
        player_id=player_id,
        transaction_id=str(uuid4()),
        currency="coins",
        new_balance=0,
        status="success",
        message="Weekly salary cost calculated",
        salary_breakdown=SalaryCalculationBreakdown(
            base_salary=float(details["base_salary"]),
            performance_bonus=float(details["performance_bonus"]),
            total=float(details["total"]),
            metrics_score=float(details["metrics_score"]),
        ),
    )


@router.post("/trigger/weekly", response_model=SalaryActionResponse)
def trigger_weekly_salary_deduction(
    player_id: str,
    metrics: PerformanceMetricsRequest,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Apply weekly salary cost as a COINS deduction to the authenticated user's wallet.
    """
    engine = SalaryEngine(db)
    perf = PerformanceMetrics(
        leads_generated=metrics.leads_generated,
        conversion_rate=metrics.conversion_rate,
        quality_score=metrics.quality_score,
        team_performance=metrics.team_performance,
    )

    fallback_user_id = int(user["user_id"])
    result = engine.apply_weekly_salary_deduction(player_id, fallback_user_id, perf)
    details = result["details"]

    if not result["ok"]:
        return SalaryActionResponse(
            player_id=player_id,
            transaction_id=str(uuid4()),
            currency="coins",
            new_balance=int(result["new_balance"]),
            status="error",
            message="Salary deduction failed: insufficient coins",
            salary_breakdown=SalaryCalculationBreakdown(
                base_salary=float(details["base_salary"]),
                performance_bonus=float(details["performance_bonus"]),
                total=float(details["total"]),
                metrics_score=float(details["metrics_score"]),
            ),
        )

    return SalaryActionResponse(
        player_id=player_id,
        transaction_id=str(uuid4()),
        currency="coins",
        new_balance=int(result["new_balance"]),
        status="success",
        message="Weekly salary deducted successfully",
        salary_breakdown=SalaryCalculationBreakdown(
            base_salary=float(details["base_salary"]),
            performance_bonus=float(details["performance_bonus"]),
            total=float(details["total"]),
            metrics_score=float(details["metrics_score"]),
        ),
    )


@router.post("/trigger/bulk", response_model=BulkSalaryDeductionResponse)
def trigger_bulk_salary_deductions(
    requests: List[BulkSalaryDeductionRequest],
    user=Depends(get_current_user),
    db=Depends(get_db),
):

    engine = SalaryEngine(db)
    fallback_user_id = int(user["user_id"])

    payload = []
    for r in requests:
        payload.append(
            {
                "player_id": r.player_id,
                "leads_generated": r.leads_generated,
                "conversion_rate": r.conversion_rate,
                "quality_score": r.quality_score,
                "team_performance": r.team_performance,
            }
        )

    results = engine.process_bulk_salary_deductions(payload, fallback_user_id)
    processed_count = len(results)
    success_count = sum(1 for v in results.values() if v)

    return BulkSalaryDeductionResponse(
        results=results,
        processed_count=processed_count,
        success_count=success_count,
    )