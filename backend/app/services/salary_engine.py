"""
Lead Salary Engine: Handles salary calculations, performance bonuses, and weekly payouts
with external contract trigger integration.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import User, Wallet, AuditLog

class PerformanceMetrics:
    """Performance metrics for bonus calculations"""
    def __init__(self, leads_generated: int = 0, conversion_rate: float = 0.0, 
                 quality_score: float = 0.0, team_performance: float = 0.0):
        self.leads_generated = leads_generated
        self.conversion_rate = conversion_rate  # 0.0 to 1.0
        self.quality_score = quality_score      # 0.0 to 100.0
        self.team_performance = team_performance # 0.0 to 100.0

class SalaryContract:
    """External contract configuration for salary calculations"""
    def __init__(self, user_id: str, base_salary: Decimal, bonus_multiplier: float = 1.0,
                 performance_threshold: float = 0.75, max_bonus_percentage: float = 0.5):
        self.user_id = user_id
        self.base_salary = base_salary
        self.bonus_multiplier = bonus_multiplier
        self.performance_threshold = performance_threshold
        self.max_bonus_percentage = max_bonus_percentage

class LeadSalaryEngine:
    def __init__(self, db: Session):
        self.db = db
        self.contracts: Dict[str, SalaryContract] = {}
        self._load_sample_contracts()
    
    def _load_sample_contracts(self):
        """Load sample contracts for demonstration"""
        self.contracts = {
            "testuser": SalaryContract(
                user_id="testuser",
                base_salary=Decimal("5000.00"),
                bonus_multiplier=1.2,
                performance_threshold=0.8,
                max_bonus_percentage=0.4
            ),
            "lead_agent_1": SalaryContract(
                user_id="lead_agent_1",
                base_salary=Decimal("4500.00"),
                bonus_multiplier=1.1,
                performance_threshold=0.75,
                max_bonus_percentage=0.35
            )
        }
    
    def register_contract(self, contract: SalaryContract):
        """Register a new salary contract"""
        self.contracts[contract.user_id] = contract
        print(f"Contract registered for user {contract.user_id} with base salary ${contract.base_salary}")
    
    def calculate_performance_bonus(self, user_id: str, metrics: PerformanceMetrics) -> Decimal:
        """Calculate performance bonus based on metrics"""
        contract = self.contracts.get(user_id)
        if not contract:
            return Decimal("0.00")
        
        # Weighted performance score calculation
        performance_score = (
            (metrics.leads_generated * 0.3) +
            (metrics.conversion_rate * 100 * 0.3) +
            (metrics.quality_score * 0.25) +
            (metrics.team_performance * 0.15)
        ) / 100.0
        
        # Apply performance threshold
        if performance_score < contract.performance_threshold:
            return Decimal("0.00")
        
        # Calculate bonus percentage
        bonus_percentage = min(
            performance_score * contract.bonus_multiplier * contract.max_bonus_percentage,
            contract.max_bonus_percentage
        )
        
        bonus_amount = contract.base_salary * Decimal(str(bonus_percentage))
        return bonus_amount.quantize(Decimal('0.01'))
    
    def calculate_weekly_payout(self, user_id: str, metrics: PerformanceMetrics) -> Dict[str, Decimal]:
        """Calculate weekly payout including base salary and performance bonus"""
        contract = self.contracts.get(user_id)
        if not contract:
            return {"base_salary": Decimal("0.00"), "performance_bonus": Decimal("0.00"), "total": Decimal("0.00")}
        
        # Weekly base salary (assuming monthly salary / 4)
        weekly_base = (contract.base_salary / 4).quantize(Decimal('0.01'))
        
        # Calculate performance bonus
        performance_bonus = self.calculate_performance_bonus(user_id, metrics)
        
        # Weekly performance bonus (distribute over 4 weeks)
        weekly_bonus = (performance_bonus / 4).quantize(Decimal('0.01'))
        
        total_payout = weekly_base + weekly_bonus
        
        return {
            "base_salary": weekly_base,
            "performance_bonus": weekly_bonus,
            "total": total_payout,
            "metrics_score": self._calculate_metrics_score(metrics)
        }
    
    def _calculate_metrics_score(self, metrics: PerformanceMetrics) -> float:
        """Calculate overall metrics score for reporting"""
        return (
            (metrics.leads_generated * 0.3) +
            (metrics.conversion_rate * 100 * 0.3) +
            (metrics.quality_score * 0.25) +
            (metrics.team_performance * 0.15)
        ) / 100.0
    
    def trigger_weekly_payout(self, user_id: str, metrics: PerformanceMetrics) -> bool:
        """Trigger weekly payout and update wallet"""
        try:
            payout_details = self.calculate_weekly_payout(user_id, metrics)
            
            # Get or create wallet for user
            wallet = self.db.execute(
                select(Wallet).where(Wallet.user_id == user_id)
            ).scalar_one_or_none()
            
            if not wallet:
                # Create dummy wallet if not exists
                wallet = Wallet(user_id=user_id, coins=0, gems=0, credits=0)
                self.db.add(wallet)
                self.db.commit()
                self.db.refresh(wallet)
            
            # Add salary as credits to wallet
            total_credits = int(payout_details["total"])
            wallet.credits += total_credits
            
            # Create audit log for salary payout
            audit_log = AuditLog(
                user_id=user_id,
                wallet_id=wallet.id,
                currency_type="credits",
                operation="salary_payout",
                amount=total_credits,
                balance_after=wallet.credits,
                meta=f"Weekly payout - Base: ${payout_details['base_salary']}, Bonus: ${payout_details['performance_bonus']}"
            )
            self.db.add(audit_log)
            self.db.commit()
            
            print(f"Weekly payout processed for {user_id}: ${payout_details['total']} (Base: ${payout_details['base_salary']}, Bonus: ${payout_details['performance_bonus']})")
            return True
            
        except Exception as e:
            print(f"Error processing payout for {user_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def get_contract_details(self, user_id: str) -> Optional[Dict]:
        """Get contract details for a user"""
        contract = self.contracts.get(user_id)
        if not contract:
            return None
        
        return {
            "user_id": contract.user_id,
            "base_salary": float(contract.base_salary),
            "bonus_multiplier": contract.bonus_multiplier,
            "performance_threshold": contract.performance_threshold,
            "max_bonus_percentage": contract.max_bonus_percentage
        }
    
    def process_bulk_payouts(self, payout_data: List[Dict]) -> Dict[str, bool]:
        """Process multiple payouts in bulk (external contract trigger simulation)"""
        results = {}
        
        for data in payout_data:
            user_id = data.get("user_id")
            metrics = PerformanceMetrics(
                leads_generated=data.get("leads_generated", 0),
                conversion_rate=data.get("conversion_rate", 0.0),
                quality_score=data.get("quality_score", 0.0),
                team_performance=data.get("team_performance", 0.0)
            )
            
            success = self.trigger_weekly_payout(user_id, metrics)
            results[user_id] = success
        
        return results
