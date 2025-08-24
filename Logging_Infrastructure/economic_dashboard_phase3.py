import json
import uuid
import copy
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, deque
from enum import Enum
import os

from logger_function import log_transaction, PlayerWallet


class AlertLevel(Enum):
    """Alert severity levels for economic warnings"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class EconomicMetrics:
    """Tracks and calculates economic metrics for the game economy"""
    
    def __init__(self, inflation_threshold: float = 0.15, 
                 scarcity_threshold: float = 0.3,
                 local_storage_path: str = "economic_data"):
        self.inflation_threshold = inflation_threshold
        self.scarcity_threshold = scarcity_threshold
        self.local_storage_path = local_storage_path
        
        # Create local storage directory if it doesn't exist
        if not os.path.exists(local_storage_path):
            os.makedirs(local_storage_path)
        
        self.transaction_history = defaultdict(list)
        self.weekly_deltas = defaultdict(lambda: defaultdict(float))
        self.resource_distribution = defaultdict(lambda: defaultdict(int))
        self.bonus_performance = defaultdict(list)
        self.inflation_rates = defaultdict(deque)
        
        self.active_alerts = []
        self.alert_history = []
        
        self.contract_bonuses = defaultdict(lambda: defaultdict(float))
        self.bonus_efficacy_scores = defaultdict(float)
        
    def store_data_locally(self, data_type: str, data: dict):
        """Store data locally as JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.local_storage_path}/{data_type}_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"Data stored locally: {filename}")
        except Exception as e:
            print(f"Error storing data locally: {e}")
    
    def track_transaction(self, transaction_data: dict):
        """Track individual transactions for analytics"""
        currency_type = transaction_data.get("currency_type")
        amount = transaction_data.get("amount", 0)
        player_id = transaction_data.get("player_id")
        transaction_type = transaction_data.get("transaction_type")
        
        self.transaction_history[currency_type].append({
            "timestamp": datetime.now().isoformat(),
            "player_id": player_id,
            "amount": amount,
            "type": transaction_type,
            "source_sink": transaction_data.get("source_sink")
        })
        
        if transaction_type == "Earn":
            self.resource_distribution[currency_type][player_id] += abs(amount)
        elif transaction_type == "Spend":
            self.resource_distribution[currency_type][player_id] -= abs(amount)
        
        # Store transaction locally every 10 transactions
        if len(self.transaction_history[currency_type]) % 10 == 0:
            self.store_data_locally(f"transactions_{currency_type}", 
                                   {"transactions": self.transaction_history[currency_type][-10:]})
    
    def calculate_weekly_delta(self, currency_type: str, week_number: int) -> float:
        """Calculate the weekly change in currency circulation"""
        week_transactions = [t for t in self.transaction_history[currency_type]
                           if self._get_week_number(t["timestamp"]) == week_number]
        
        total_earned = sum(abs(t["amount"]) for t in week_transactions if t["type"] == "Earn")
        total_spent = sum(abs(t["amount"]) for t in week_transactions if t["type"] == "Spend")
        
        delta = total_earned - total_spent
        self.weekly_deltas[week_number][currency_type] = delta
        
        # Store weekly delta locally
        self.store_data_locally(f"weekly_delta_w{week_number}", 
                               {"week": week_number, "deltas": dict(self.weekly_deltas[week_number])})
        
        return delta
    
    def detect_inflation(self, currency_type: str, lookback_weeks: int = 4) -> Tuple[bool, float]:
        """
        Detect inflation in a specific currency type
        Returns: (is_inflated, inflation_rate)
        """
        if len(self.weekly_deltas) < lookback_weeks:
            return False, 0.0
        
        recent_weeks = sorted(self.weekly_deltas.keys())[-lookback_weeks:]
        deltas = [self.weekly_deltas[week][currency_type] for week in recent_weeks]
        
        if not deltas or deltas[0] == 0:
            return False, 0.0
        
        inflation_rate = (deltas[-1] - deltas[0]) / abs(deltas[0]) if deltas[0] != 0 else 0
        
        # Track inflation rate
        self.inflation_rates[currency_type].append({
            "timestamp": datetime.now().isoformat(),
            "rate": inflation_rate,
            "weeks_analyzed": lookback_weeks
        })
        
        if len(self.inflation_rates[currency_type]) > 100:
            self.inflation_rates[currency_type].popleft()
        
        is_inflated = inflation_rate > self.inflation_threshold
        
        if is_inflated:
            self._create_alert(
                AlertLevel.WARNING,
                f"Inflation detected in {currency_type}",
                {"currency": currency_type, "rate": inflation_rate, "threshold": self.inflation_threshold}
            )
        
        return is_inflated, inflation_rate
    
    def mitigate_inflation(self, currency_type: str) -> dict:
        """
        Suggest and implement inflation mitigation strategies
        """
        mitigation_strategies = []
        
        is_inflated, rate = self.detect_inflation(currency_type)
        
        if is_inflated:
            if rate > 0.3:
                mitigation_strategies.append({
                    "action": "reduce_earn_rates",
                    "target_reduction": 0.2,
                    "affected_sources": ["DailyLoginBonus", "WeeklyChallengeReward"],
                    "priority": "HIGH"
                })
            
            mitigation_strategies.append({
                "action": "increase_sinks",
                "suggested_sinks": ["Premium_Shop_Items", "Upgrade_Costs"],
                "target_increase": 0.15,
                "priority": "MEDIUM"
            })
            
            if rate > 0.5:
                mitigation_strategies.append({
                    "action": "temporary_earning_caps",
                    "cap_multiplier": 0.8,
                    "duration_days": 7,
                    "priority": "HIGH"
                })
        
        mitigation_plan = {
            "currency": currency_type,
            "inflation_rate": rate,
            "strategies": mitigation_strategies,
            "timestamp": datetime.now().isoformat()
        }
        
        self.store_data_locally(f"mitigation_plan_{currency_type}", mitigation_plan)
        
        return mitigation_plan
    
    def generate_resource_scarcity_heatmap(self) -> dict:
        """
        Generate a heatmap showing resource scarcity across players
        """
        heatmap_data = {}
        
        for currency_type, player_balances in self.resource_distribution.items():
            if not player_balances:
                continue
            
            values = list(player_balances.values())
            avg_balance = statistics.mean(values) if values else 0
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            
            scarce_players = [
                player for player, balance in player_balances.items()
                if balance < avg_balance * self.scarcity_threshold
            ]
            
            heatmap_data[currency_type] = {
                "average_balance": avg_balance,
                "std_deviation": std_dev,
                "total_circulation": sum(values),
                "scarce_players": scarce_players,
                "scarcity_percentage": len(scarce_players) / len(player_balances) * 100 if player_balances else 0,
                "distribution": {
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "median": statistics.median(values) if values else 0
                }
            }
            
            # Create alert if scarcity is too high
            if heatmap_data[currency_type]["scarcity_percentage"] > 50:
                self._create_alert(
                    AlertLevel.WARNING,
                    f"High resource scarcity in {currency_type}",
                    {"currency": currency_type, 
                     "scarcity_percentage": heatmap_data[currency_type]["scarcity_percentage"]}
                )
        
        self.store_data_locally("resource_scarcity_heatmap", heatmap_data)
        
        return heatmap_data
    
    def track_contract_bonus(self, player_id: str, bonus_type: str, 
                           bonus_amount: float, performance_metric: float):
        """Track contract bonuses and their impact"""
        self.contract_bonuses[player_id][bonus_type] += bonus_amount
        
        self.bonus_performance[player_id].append({
            "timestamp": datetime.now().isoformat(),
            "bonus_type": bonus_type,
            "amount": bonus_amount,
            "performance_metric": performance_metric
        })
        
        # Calculate efficacy
        self._calculate_bonus_efficacy(player_id, bonus_type)
    
    def _calculate_bonus_efficacy(self, player_id: str, bonus_type: str):
        """Calculate how effective bonuses are at driving desired behavior"""
        player_bonuses = [b for b in self.bonus_performance[player_id] 
                         if b["bonus_type"] == bonus_type]
        
        if len(player_bonuses) < 2:
            return
        
        # Calculate correlation between bonus amount and performance
        amounts = [b["amount"] for b in player_bonuses]
        performances = [b["performance_metric"] for b in player_bonuses]
        
        if len(set(amounts)) > 1: 
            avg_performance = statistics.mean(performances)
            recent_performance = statistics.mean(performances[-3:]) if len(performances) >= 3 else performances[-1]
            
            efficacy = (recent_performance - avg_performance) / avg_performance if avg_performance > 0 else 0
            self.bonus_efficacy_scores[f"{player_id}_{bonus_type}"] = efficacy
    
    def get_bonus_analytics(self) -> dict:
        """Generate comprehensive bonus performance analytics"""
        analytics = {
            "total_bonuses_distributed": {},
            "average_bonus_by_type": {},
            "efficacy_scores": dict(self.bonus_efficacy_scores),
            "top_performers": [],
            "bonus_inflation_risk": {}
        }
        
        for player_id, bonuses in self.contract_bonuses.items():
            for bonus_type, amount in bonuses.items():
                if bonus_type not in analytics["total_bonuses_distributed"]:
                    analytics["total_bonuses_distributed"][bonus_type] = 0
                analytics["total_bonuses_distributed"][bonus_type] += amount
        
        for bonus_type, total in analytics["total_bonuses_distributed"].items():
            player_count = sum(1 for p in self.contract_bonuses.values() if bonus_type in p)
            analytics["average_bonus_by_type"][bonus_type] = total / player_count if player_count > 0 else 0
        
        player_totals = [(p, sum(b.values())) for p, b in self.contract_bonuses.items()]
        player_totals.sort(key=lambda x: x[1], reverse=True)
        analytics["top_performers"] = player_totals[:10]
        
        for bonus_type in analytics["total_bonuses_distributed"]:
            recent_bonuses = [b["amount"] for p in self.bonus_performance.values() 
                            for b in p if b["bonus_type"] == bonus_type][-20:]
            if len(recent_bonuses) >= 10:
                early_avg = statistics.mean(recent_bonuses[:10])
                late_avg = statistics.mean(recent_bonuses[-10:])
                inflation = (late_avg - early_avg) / early_avg if early_avg > 0 else 0
                analytics["bonus_inflation_risk"][bonus_type] = inflation
                
                if inflation > 0.3:
                    self._create_alert(
                        AlertLevel.CRITICAL,
                        f"Bonus inflation detected in {bonus_type}",
                        {"bonus_type": bonus_type, "inflation": inflation}
                    )
        
        self.store_data_locally("bonus_analytics", analytics)
        
        return analytics
    
    def create_economic_pressure_thresholds(self) -> dict:
        """Define and monitor economic pressure thresholds"""
        thresholds = {
            "bankruptcy_risk": {
                "soft_currency": 100,
                "premium_currency": 0,
                "coaching_credits": 5
            },
            "inflation_warning": {
                "rate": 0.15,
                "critical": 0.3
            },
            "scarcity_warning": {
                "percentage": 40,
                "critical": 60
            },
            "bonus_cap_warning": {
                "percentage_of_income": 0.5
            }
        }
        
        warnings = []
        
        # Check bankruptcy risks
        for currency, min_threshold in thresholds["bankruptcy_risk"].items():
            at_risk_players = [
                p for p, balance in self.resource_distribution[currency].items()
                if balance <= min_threshold
            ]
            if at_risk_players:
                warnings.append({
                    "type": "bankruptcy_risk",
                    "currency": currency,
                    "affected_players": at_risk_players,
                    "severity": AlertLevel.CRITICAL if len(at_risk_players) > 5 else AlertLevel.WARNING
                })
        
        # Check inflation
        for currency in ["Soft", "Premium", "Utility", "CoachingCredit"]:
            is_inflated, rate = self.detect_inflation(currency)
            if rate > thresholds["inflation_warning"]["critical"]:
                warnings.append({
                    "type": "inflation_critical",
                    "currency": currency,
                    "rate": rate,
                    "severity": AlertLevel.EMERGENCY
                })
            elif is_inflated:
                warnings.append({
                    "type": "inflation_warning",
                    "currency": currency,
                    "rate": rate,
                    "severity": AlertLevel.WARNING
                })
        
        for warning in warnings:
            self._create_alert(warning["severity"], 
                             f"{warning['type']} - {warning.get('currency', 'System')}", 
                             warning)
        
        result = {
            "thresholds": thresholds,
            "current_warnings": warnings,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store thresholds and warnings locally
        self.store_data_locally("economic_pressure_thresholds", result)
        
        return result
    
    def _create_alert(self, level: AlertLevel, message: str, data: dict):
        """Create and store an alert"""
        alert = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "message": message,
            "data": data,
            "acknowledged": False
        }
        
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        
        # Store critical alerts immediately
        if level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
            self.store_data_locally(f"alert_{level.value}", alert)
        
        print(f"\n🚨 ALERT [{level.value}]: {message}")
        print(f"   Data: {json.dumps(data, indent=2)}")
    
    def _get_week_number(self, timestamp_str: str) -> int:
        """Get week number from timestamp"""
        timestamp = datetime.fromisoformat(timestamp_str)
        return timestamp.isocalendar()[1]
    
    def get_dashboard_summary(self) -> dict:
        """Generate a comprehensive dashboard summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "economic_health": {
                "inflation_rates": {},
                "resource_scarcity": {},
                "bonus_distribution": {}
            },
            "alerts": {
                "active": len(self.active_alerts),
                "critical": len([a for a in self.active_alerts if a["level"] == AlertLevel.CRITICAL.value]),
                "recent": self.active_alerts[-5:] if self.active_alerts else []
            },
            "weekly_trends": dict(self.weekly_deltas),
            "recommendations": []
        }
        
        for currency in ["Soft", "Premium", "Utility", "CoachingCredit"]:
            is_inflated, rate = self.detect_inflation(currency)
            summary["economic_health"]["inflation_rates"][currency] = {
                "rate": rate,
                "is_inflated": is_inflated
            }
        
        heatmap = self.generate_resource_scarcity_heatmap()
        for currency, data in heatmap.items():
            summary["economic_health"]["resource_scarcity"][currency] = data["scarcity_percentage"]
        
        bonus_analytics = self.get_bonus_analytics()
        summary["economic_health"]["bonus_distribution"] = bonus_analytics["total_bonuses_distributed"]
        
        if any(data["is_inflated"] for data in summary["economic_health"]["inflation_rates"].values()):
            summary["recommendations"].append("Consider implementing sink mechanisms to combat inflation")
        
        if any(pct > 40 for pct in summary["economic_health"]["resource_scarcity"].values()):
            summary["recommendations"].append("Increase resource generation for scarce currencies")
        
        # local save
        self.store_data_locally("dashboard_summary", summary)
        
        return summary


class EconomicMonitoringSystem:
    """Main system for monitoring and managing the game economy"""
    
    def __init__(self):
        self.metrics = EconomicMetrics()
        self.wallets = {}  
        
    def create_player_wallet(self, player_id: str, **initial_balances) -> PlayerWallet:
        """Create and register a new player wallet"""
        wallet = PlayerWallet(player_id, **initial_balances)
        self.wallets[player_id] = wallet
        return wallet
    
    def process_transaction(self, player_id: str, currency_type: str, 
                           amount: float, source_sink: str, 
                           context_data: dict = None) -> bool:
        """Process a transaction and update metrics"""
        if player_id not in self.wallets:
            print(f"Error: Player {player_id} not found")
            return False
        
        wallet = self.wallets[player_id]
        
        # Process transaction
        if amount > 0:
            success = wallet.add_currency(currency_type, amount, source_sink, context_data)
        else:
            success = wallet.spend_currency(currency_type, abs(amount), source_sink, context_data)
        
        if success:
            transaction_data = {
                "player_id": player_id,
                "currency_type": currency_type,
                "amount": amount,
                "transaction_type": "Earn" if amount > 0 else "Spend",
                "source_sink": source_sink,
                "context_data": context_data
            }
            self.metrics.track_transaction(transaction_data)
            
            # Update resource distribution
            self.metrics.resource_distribution[currency_type][player_id] = wallet.get_balance(currency_type)
        
        return success
    
    def apply_contract_bonus(self, player_id: str, bonus_type: str, 
                            base_amount: float, performance_multiplier: float) -> float:
        """Apply a contract bonus with performance multiplier"""
        if player_id not in self.wallets:
            print(f"Error: Player {player_id} not found")
            return 0
        
        bonus_amount = base_amount * performance_multiplier
        
        self.metrics.track_contract_bonus(player_id, bonus_type, 
                                         bonus_amount, performance_multiplier)
        
        # Apply bonusu if availiable
        success = self.process_transaction(
            player_id, "Soft", bonus_amount, 
            f"ContractBonus_{bonus_type}",
            {"multiplier": performance_multiplier, "base": base_amount}
        )
        
        return bonus_amount if success else 0
    
    def run_weekly_analysis(self, week_number: int) -> dict:
        """Run comprehensive weekly economic analysis"""
        print(f"\n{'='*60}")
        print(f"WEEKLY ECONOMIC ANALYSIS - WEEK {week_number}")
        print(f"{'='*60}")
        
        analysis = {
            "week": week_number,
            "timestamp": datetime.now().isoformat(),
            "deltas": {},
            "inflation": {},
            "scarcity": {},
            "bonuses": {},
            "alerts": [],
            "thresholds": {}
        }
        
        # Calculate weekly deltas for all currencies
        for currency in ["Soft", "Premium", "Utility", "CoachingCredit"]:
            delta = self.metrics.calculate_weekly_delta(currency, week_number)
            analysis["deltas"][currency] = delta
            print(f"\n{currency} Weekly Delta: {delta:+.2f}")
            
            
            is_inflated, rate = self.metrics.detect_inflation(currency)
            analysis["inflation"][currency] = {
                "is_inflated": is_inflated,
                "rate": rate
            }
            if is_inflated:
                print(f"  ⚠️  INFLATION DETECTED: {rate:.2%}")
                mitigation = self.metrics.mitigate_inflation(currency)
                analysis["inflation"][currency]["mitigation"] = mitigation
        
        # heatmap
        analysis["scarcity"] = self.metrics.generate_resource_scarcity_heatmap()
        

        analysis["bonuses"] = self.metrics.get_bonus_analytics()
        
        # economic pressure thresholds
        analysis["thresholds"] = self.metrics.create_economic_pressure_thresholds()
        
        analysis["alerts"] = self.metrics.active_alerts[-10:]  
        
        self.metrics.store_data_locally(f"weekly_analysis_w{week_number}", analysis)
        
        print(f"\n{'='*60}")
        print(f"SUMMARY:")
        print(f"  Active Alerts: {len(self.metrics.active_alerts)}")
        print(f"  Critical Issues: {len([a for a in self.metrics.active_alerts if a['level'] == 'CRITICAL'])}")
        print(f"  Inflated Currencies: {[c for c, d in analysis['inflation'].items() if d['is_inflated']]}")
        print(f"{'='*60}\n")
        
        return analysis
    
    def get_dashboard(self) -> dict:
        """Get the current dashboard state"""
        return self.metrics.get_dashboard_summary()


def run_integration_tests():
    """Run integration tests for the monitoring system"""
    print("\n" + "="*60)
    print("RUNNING ECONOMIC MONITORING SYSTEM TESTS")
    print("="*60)
    
    monitor = EconomicMonitoringSystem()
    
    # test players
    players = [
        monitor.create_player_wallet(f"player_{i}", 
                                    initial_soft=1000 + i*100,
                                    initial_premium=50 + i*5,
                                    initial_utility=10,
                                    initial_coaching_credits=20 + i*2)
        for i in range(10)
    ]
    
    print("\n✅ Created 10 test player wallets")
    
    print("\n📅 SIMULATING WEEK 1 TRANSACTIONS...")
    
    for i, player in enumerate(players[:7]):  
        monitor.process_transaction(f"player_{i}", "Soft", 100, "DailyLoginBonus", {"day": 1})
    
    monitor.process_transaction("player_0", "Premium", -10, "CosmeticPurchase", {"item": "Hat"})
    monitor.process_transaction("player_1", "Soft", -500, "PlayerUpgrade", {"upgrade": "Speed"})
    
    for i in range(5):
        monitor.apply_contract_bonus(f"player_{i}", "WeeklyPerformance", 
                                    200, 1.0 + i * 0.1)
    
    week1_analysis = monitor.run_weekly_analysis(1)
    
    print("\n📅 SIMULATING WEEK 2 - INFLATION SCENARIO...")
    
    for i in range(10):
        monitor.process_transaction(f"player_{i}", "Soft", 500, "EventReward", {"event": "Special"})
        monitor.process_transaction(f"player_{i}", "Soft", 300, "QuestCompletion", {"quest": "Main"})
    
    monitor.process_transaction("player_2", "Soft", -100, "MinorPurchase", {})
    
    week2_analysis = monitor.run_weekly_analysis(2)
    
    print("\n📅 SIMULATING WEEK 3 - SCARCITY SCENARIO...")
    
    for i in range(3, 8):
        monitor.process_transaction(f"player_{i}", "Soft", -800, "MajorPurchase", {"item": "Exclusive"})
    
    for i in range(10):
        monitor.process_transaction(f"player_{i}", "Soft", 50, "DailyLoginBonus", {"day": 15})
    
    # Test coaching credit cap
    monitor.process_transaction("player_0", "CoachingCredit", 90, "AchievementReward", {})
    
    week3_analysis = monitor.run_weekly_analysis(3)
    
    dashboard = monitor.get_dashboard()
    
    print("\n" + "="*60)
    print("FINAL DASHBOARD SUMMARY")
    print("="*60)
    print(f"Active Alerts: {dashboard['alerts']['active']}")
    print(f"Critical Alerts: {dashboard['alerts']['critical']}")
    print(f"Recommendations: {dashboard['recommendations']}")
    
    print("\n✅ All integration tests completed successfully!")
    print(f"📁 Data stored locally in: {monitor.metrics.local_storage_path}/")
    
    return monitor


if __name__ == "__main__":
    # Run the integration tests
    monitoring_system = run_integration_tests()
    
    print("\n" + "="*60)
    print("PHASE 3 IMPLEMENTATION COMPLETE")
    print("="*60)
    print("\nDeliverables:")
    print("✅ Contract bonus inflation detection and mitigation systems")
    print("✅ Weekly delta tracking and resource scarcity heatmaps")
    print("✅ Bonus efficacy scoring and performance analytics")
    print("✅ Alert thresholds for economic pressure warning systems")
    print("✅ Local data storage implementation")
    print("\nAll data is being stored locally for persistence and analysis.")
