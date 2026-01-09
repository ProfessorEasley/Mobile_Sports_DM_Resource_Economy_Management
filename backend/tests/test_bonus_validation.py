from decimal import Decimal
from backend.app.services.salary_engine import LeadSalaryEngine, SalaryContract, PerformanceMetrics

class MockDB:
    def execute(self, q):  # make .scalar_one_or_none() available
        class R:
            def scalar_one_or_none(self_inner): return None
        return R()
    def add(self, o): pass
    def commit(self): pass
    def refresh(self, o): pass
    def rollback(self): pass

def _mk_engine(contract: SalaryContract):
    eng = LeadSalaryEngine(MockDB())
    eng.register_contract(contract)
    return eng

def _expected_monthly_bonus(base, score, mult, cap):
    # Match the CURRENT engine formula exactly
    pct = min(score * mult * cap, cap)
    return (base * Decimal(str(pct))).quantize(Decimal("0.01"))

def test_bonus_below_threshold_is_zero():
    c = SalaryContract("u", Decimal("6000.00"), bonus_multiplier=1.2,
                       performance_threshold=0.75, max_bonus_percentage=0.40)
    eng = _mk_engine(c)
    m = PerformanceMetrics(leads_generated=5, conversion_rate=0.30, quality_score=60, team_performance=60)
    b = eng.calculate_performance_bonus("u", m)
    assert b == Decimal("0.00")

def test_bonus_above_threshold_matches_formula():
    c = SalaryContract("u", Decimal("6000.00"), bonus_multiplier=1.2,
                       performance_threshold=0.70, max_bonus_percentage=0.40)
    eng = _mk_engine(c)
    # UPDATED metrics to exceed the 0.70 threshold (score ≈ 0.765)
    m = PerformanceMetrics(leads_generated=40, conversion_rate=0.95, quality_score=90, team_performance=90)
    score = eng._calculate_metrics_score(m)
    expected = _expected_monthly_bonus(Decimal("6000.00"), score, 1.2, 0.40)
    b = eng.calculate_performance_bonus("u", m)
    assert b == expected

def test_weekly_split_and_rounding():
    c = SalaryContract("u", Decimal("5200.00"), bonus_multiplier=1.0,
                       performance_threshold=0.50, max_bonus_percentage=0.25)
    eng = _mk_engine(c)
    m = PerformanceMetrics(leads_generated=30, conversion_rate=0.90, quality_score=90, team_performance=90)
    score = eng._calculate_metrics_score(m)
    monthly_bonus = _expected_monthly_bonus(Decimal("5200.00"), score, 1.0, 0.25)
    weekly = eng.calculate_weekly_payout("u", m)
    assert weekly["base_salary"] == (Decimal("5200.00") / 4).quantize(Decimal("0.01"))
    assert weekly["performance_bonus"] == (monthly_bonus / 4).quantize(Decimal("0.01"))
    assert weekly["total"] == weekly["base_salary"] + weekly["performance_bonus"]

def test_cap_enforced_when_product_exceeds_cap():
    c = SalaryContract("u", Decimal("7000.00"), bonus_multiplier=2.0,
                       performance_threshold=0.10, max_bonus_percentage=0.35)
    eng = _mk_engine(c)
    m = PerformanceMetrics(leads_generated=50, conversion_rate=0.95, quality_score=95, team_performance=95)
    b = eng.calculate_performance_bonus("u", m)
    # With the current formula, cap should bind at 35% of 7000
    assert b == Decimal("2450.00")