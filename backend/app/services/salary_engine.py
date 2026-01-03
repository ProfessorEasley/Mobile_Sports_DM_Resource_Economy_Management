from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Wallet, AuditLog


@dataclass(frozen=True)
class PerformanceMetrics:
    leads_generated: int = 0
    conversion_rate: float = 0.0  # 0.0 to 1.0
    quality_score: float = 0.0    # 0.0 to 100.0
    team_performance: float = 0.0 # 0.0 to 100.0


@dataclass(frozen=True)
class SalaryContract:
    player_id: str
    base_salary: Decimal
    bonus_multiplier: float = 1.0
    performance_threshold: float = 0.75
    max_bonus_percentage: float = 0.5


class SalaryEngine:
    _contracts_store: Dict[str, SalaryContract] = {}  # shared across instances

    def __init__(self, db: Session):
        self.db = db
        self.contracts = SalaryEngine._contracts_store
        self._load_sample_contracts()

    def _load_sample_contracts(self) -> None:
        if "lead_001" not in self.contracts:
            self.contracts["lead_001"] = SalaryContract(
                player_id="lead_001",
                base_salary=Decimal("5000.00"),
                bonus_multiplier=1.2,
                performance_threshold=0.75,
                max_bonus_percentage=0.5,
            )

    @staticmethod
    def _normalize_player_id(player_id: str) -> str:
        return str(player_id).strip()

    def register_contract(self, contract: SalaryContract) -> bool:
        try:
            pid = self._normalize_player_id(contract.player_id)
            self.contracts[pid] = SalaryContract(
                player_id=pid,
                base_salary=contract.base_salary,
                bonus_multiplier=contract.bonus_multiplier,
                performance_threshold=contract.performance_threshold,
                max_bonus_percentage=contract.max_bonus_percentage,
            )
            return True
        except Exception:
            return False

    def get_contract_details(self, player_id: str) -> Optional[Dict]:
        pid = self._normalize_player_id(player_id)
        c = self.contracts.get(pid)
        if not c:
            return None
        return {
            "player_id": c.player_id,
            "base_salary": float(c.base_salary),
            "bonus_multiplier": c.bonus_multiplier,
            "performance_threshold": c.performance_threshold,
            "max_bonus_percentage": c.max_bonus_percentage,
        }

    def _calculate_metrics_score(self, metrics: PerformanceMetrics) -> float:
        leads_score = min(metrics.leads_generated / 100.0, 1.0)
        conversion_score = max(0.0, min(metrics.conversion_rate, 1.0))
        quality_score = max(0.0, min(metrics.quality_score, 100.0)) / 100.0
        team_score = max(0.0, min(metrics.team_performance, 100.0)) / 100.0

        return (
            leads_score * 0.3
            + conversion_score * 0.3
            + quality_score * 0.25
            + team_score * 0.15
        )

    def calculate_performance_bonus(self, player_id: str, metrics: PerformanceMetrics) -> Decimal:
        pid = self._normalize_player_id(player_id)
        contract = self.contracts.get(pid)
        if not contract:
            raise ValueError(f"No salary contract found for player_id={pid}")

        score = self._calculate_metrics_score(metrics)
        if score < contract.performance_threshold:
            return Decimal("0.00")

        bonus_pct = min(
            score * contract.bonus_multiplier * contract.max_bonus_percentage,
            contract.max_bonus_percentage,
        )
        bonus_amount = (contract.base_salary * Decimal(str(bonus_pct))).quantize(Decimal("0.01"))
        return bonus_amount

    def calculate_weekly_salary_cost(self, player_id: str, metrics: PerformanceMetrics) -> Dict[str, Decimal]:
        pid = self._normalize_player_id(player_id)
        contract = self.contracts.get(pid)
        if not contract:
            raise ValueError(f"No salary contract found for player_id={pid}")

        weekly_base = (contract.base_salary / Decimal("4")).quantize(Decimal("0.01"))
        performance_bonus = self.calculate_performance_bonus(pid, metrics)
        weekly_bonus = (performance_bonus / Decimal("4")).quantize(Decimal("0.01"))
        total_weekly = (weekly_base + weekly_bonus).quantize(Decimal("0.01"))
        metrics_score = Decimal(str(self._calculate_metrics_score(metrics))).quantize(Decimal("0.001"))

        return {
            "base_salary": weekly_base,
            "performance_bonus": weekly_bonus,
            "total": total_weekly,
            "metrics_score": metrics_score,
        }

    def apply_weekly_salary_deduction(
        self,
        player_id: str,
        fallback_user_id: int,
        metrics: PerformanceMetrics,
    ) -> Dict[str, object]:
        
        details = self.calculate_weekly_salary_cost(player_id, metrics)
        total_cost_coins = int(details["total"])

        wallet = self.db.execute(
            select(Wallet).where(Wallet.user_id == fallback_user_id)
        ).scalar_one_or_none()

        if not wallet:
            wallet = Wallet(user_id=fallback_user_id, coins=0, gems=0, credits=0)
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)

        if wallet.coins < total_cost_coins:
            self.db.rollback()
            return {
                "ok": False,
                "reason": "insufficient_funds",
                "new_balance": int(wallet.coins),
                "details": details,
            }

        wallet.coins -= total_cost_coins
        new_balance = int(wallet.coins)

        audit = AuditLog(
            user_id=fallback_user_id,
            wallet_id=wallet.id,
            currency_type="coins",
            operation="salary_deduction",
            amount=total_cost_coins,
            balance_after=new_balance,
            meta={
                "player_id": str(player_id),
                "base_salary_weekly": str(details["base_salary"]),
                "performance_bonus_weekly": str(details["performance_bonus"]),
                "metrics_score": str(details["metrics_score"]),
            },
        )
        self.db.add(audit)
        self.db.commit()

        return {
            "ok": True,
            "new_balance": new_balance,
            "details": details,
        }

    def process_bulk_salary_deductions(
        self,
        items: List[Dict],
        fallback_user_id: int,
    ) -> Dict[str, bool]:

        results: Dict[str, bool] = {}
        for item in items:
            pid = self._normalize_player_id(item.get("player_id", ""))
            metrics = PerformanceMetrics(
                leads_generated=int(item.get("leads_generated", 0)),
                conversion_rate=float(item.get("conversion_rate", 0.0)),
                quality_score=float(item.get("quality_score", 0.0)),
                team_performance=float(item.get("team_performance", 0.0)),
            )
            try:
                res = self.apply_weekly_salary_deduction(pid, fallback_user_id, metrics)
                results[pid] = bool(res.get("ok"))
            except Exception:
                results[pid] = False
        return results