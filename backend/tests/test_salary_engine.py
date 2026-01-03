from decimal import Decimal


def test_weekly_cost_calculation_smoke():
    from backend.app.services.salary_engine import SalaryEngine, PerformanceMetrics, SalaryContract

    class DummyDB:
        pass

    engine = SalaryEngine(db=DummyDB())  # sample contracts loaded
    engine.register_contract(
        SalaryContract(
            player_id="p1",
            base_salary=Decimal("4000.00"),
            bonus_multiplier=1.0,
            performance_threshold=0.0,
            max_bonus_percentage=0.5,
        )
    )

    metrics = PerformanceMetrics(
        leads_generated=100,
        conversion_rate=1.0,
        quality_score=100.0,
        team_performance=100.0,
    )

    details = engine.calculate_weekly_salary_cost("p1", metrics)
    assert "total" in details
    assert float(details["total"]) > 0.0