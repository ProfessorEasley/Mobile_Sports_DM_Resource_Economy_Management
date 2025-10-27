"""
Test script for Lead Salary Engine functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.salary_engine import LeadSalaryEngine, PerformanceMetrics, SalaryContract
from decimal import Decimal

def test_salary_engine():
    """Test the salary engine functionality"""
    print("=== Lead Salary Engine Test ===\n")
    
    # Mock database session (for testing without actual DB)
    class MockDB:
        def execute(self, query):
            return None
        def add(self, obj):
            pass
        def commit(self):
            pass
        def refresh(self, obj):
            pass
        def rollback(self):
            pass
    
    # Initialize salary engine
    engine = LeadSalaryEngine(MockDB())
    
    # Test 1: Contract Registration
    print("1. Testing Contract Registration:")
    new_contract = SalaryContract(
        user_id="test_agent_1",
        base_salary=Decimal("6000.00"),
        bonus_multiplier=1.3,
        performance_threshold=0.85,
        max_bonus_percentage=0.6
    )
    engine.register_contract(new_contract)
    
    # Test 2: Performance Metrics and Bonus Calculation
    print("\n2. Testing Performance Bonus Calculation:")
    high_performance = PerformanceMetrics(
        leads_generated=25,
        conversion_rate=0.85,
        quality_score=92.0,
        team_performance=88.0
    )
    
    bonus = engine.calculate_performance_bonus("test_agent_1", high_performance)
    print(f"High Performance Bonus: ${bonus}")
    
    low_performance = PerformanceMetrics(
        leads_generated=8,
        conversion_rate=0.45,
        quality_score=65.0,
        team_performance=70.0
    )
    
    bonus_low = engine.calculate_performance_bonus("test_agent_1", low_performance)
    print(f"Low Performance Bonus: ${bonus_low}")
    
    # Test 3: Weekly Payout Calculation
    print("\n3. Testing Weekly Payout Calculation:")
    payout_high = engine.calculate_weekly_payout("test_agent_1", high_performance)
    print(f"High Performance Payout:")
    print(f"  Base Salary: ${payout_high['base_salary']}")
    print(f"  Performance Bonus: ${payout_high['performance_bonus']}")
    print(f"  Total: ${payout_high['total']}")
    print(f"  Metrics Score: {payout_high['metrics_score']:.2f}")
    
    payout_low = engine.calculate_weekly_payout("test_agent_1", low_performance)
    print(f"\nLow Performance Payout:")
    print(f"  Base Salary: ${payout_low['base_salary']}")
    print(f"  Performance Bonus: ${payout_low['performance_bonus']}")
    print(f"  Total: ${payout_low['total']}")
    print(f"  Metrics Score: {payout_low['metrics_score']:.2f}")
    
    # Test 4: Contract Details
    print("\n4. Testing Contract Details Retrieval:")
    contract_details = engine.get_contract_details("test_agent_1")
    if contract_details:
        print(f"Contract for test_agent_1:")
        for key, value in contract_details.items():
            print(f"  {key}: {value}")
    
    # Test 5: Bulk Payout Simulation
    print("\n5. Testing Bulk Payout Processing:")
    bulk_data = [
        {
            "user_id": "testuser",
            "leads_generated": 20,
            "conversion_rate": 0.75,
            "quality_score": 85.0,
            "team_performance": 80.0
        },
        {
            "user_id": "test_agent_1",
            "leads_generated": 25,
            "conversion_rate": 0.85,
            "quality_score": 92.0,
            "team_performance": 88.0
        }
    ]
    
    # Note: This would fail in actual testing without proper DB setup
    # results = engine.process_bulk_payouts(bulk_data)
    # print(f"Bulk payout results: {results}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_salary_engine()
