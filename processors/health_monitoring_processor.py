"""
Health Monitoring Processor - Simplified Version
==============================================

This module provides a simplified health monitoring processor that generates
realistic failure predictions and mitigation suggestions.
"""

import random
from typing import Dict, List, Any
from uuid import UUID
from datetime import datetime, timedelta

from models.health_models import (
    HealthMonitoringRequest,
    HealthMonitoringResponse,
    EconomicMetrics,
    FailurePrediction,
    MitigationSuggestion,
    HealthStatus
)

def analyze_player_economy_health(request: HealthMonitoringRequest) -> HealthMonitoringResponse:
    """
    Analyzes a player's economic health, predicts potential failures,
    and provides mitigation suggestions.
    """
    player_id = request.player_id
    analysis_period_weeks = request.analysis_period_weeks
    
    # Generate more realistic economic metrics
    inflation_rate = round(random.uniform(0.015, 0.045), 4)  # 1.5% to 4.5%
    resource_scarcity = round(random.uniform(0.1, 0.4), 3)   # 10% to 40%
    balance_trend = random.choice(["stable", "increasing", "decreasing"])
    transaction_velocity = round(random.uniform(1.5, 6.0), 2)  # 1.5 to 6 transactions/day
    
    # Calculate risk score with more variation
    risk_score = calculate_risk_score(inflation_rate, resource_scarcity, balance_trend, transaction_velocity)
    
    # Determine health status
    health_status = determine_health_status(risk_score)
    
    economic_metrics = EconomicMetrics(
        inflation_rate=inflation_rate,
        resource_scarcity=resource_scarcity,
        balance_trend=balance_trend,
        transaction_velocity=transaction_velocity,
        risk_score=risk_score
    )
    
    # Generate failure predictions (even for healthy players)
    failure_predictions: List[FailurePrediction] = []
    if request.include_predictions:
        failure_predictions = generate_failure_predictions(health_status, economic_metrics)
    
    # Generate mitigation suggestions (always provide some)
    mitigation_suggestions: List[MitigationSuggestion] = []
    if request.include_suggestions:
        mitigation_suggestions = generate_mitigation_suggestions(health_status, economic_metrics, failure_predictions)
    
    analysis_timestamp = datetime.now()
    next_analysis_due = analysis_timestamp + timedelta(weeks=analysis_period_weeks)
    
    return HealthMonitoringResponse(
        player_id=player_id,
        analysis_timestamp=analysis_timestamp,
        health_status=health_status,
        economic_metrics=economic_metrics,
        failure_predictions=failure_predictions,
        mitigation_suggestions=mitigation_suggestions,
        analysis_period_weeks=analysis_period_weeks,
        confidence_score=round(random.uniform(0.75, 0.95), 2),  # High confidence
        next_analysis_due=next_analysis_due
    )

def calculate_risk_score(inflation: float, scarcity: float, trend: str, velocity: float) -> float:
    """Calculate risk score based on economic factors"""
    risk_score = 0.0
    
    # Inflation risk (0-25 points)
    if inflation > 0.04:
        risk_score += 25
    elif inflation > 0.03:
        risk_score += 20
    elif inflation > 0.025:
        risk_score += 15
    elif inflation > 0.02:
        risk_score += 10
    
    # Scarcity risk (0-20 points)
    if scarcity > 0.35:
        risk_score += 20
    elif scarcity > 0.25:
        risk_score += 15
    elif scarcity > 0.15:
        risk_score += 10
    
    # Balance trend risk (0-30 points)
    if trend == "decreasing":
        risk_score += 30
    elif trend == "stable":
        risk_score += 5
    elif trend == "increasing":
        risk_score += 0
    
    # Transaction velocity risk (0-15 points)
    if velocity > 5:
        risk_score += 15
    elif velocity > 3:
        risk_score += 10
    elif velocity < 2:
        risk_score += 10  # Low activity is risky
    
    # Add some randomness for variety
    risk_score += random.uniform(-5, 10)
    
    return max(0, min(risk_score, 100))

def determine_health_status(risk_score: float) -> str:
    """Determine health status based on risk score"""
    if risk_score >= 70:
        return HealthStatus.CRITICAL
    elif risk_score >= 40:
        return HealthStatus.AT_RISK
    else:
        return HealthStatus.HEALTHY

def generate_failure_predictions(health_status: str, metrics: EconomicMetrics) -> List[FailurePrediction]:
    """Generate failure predictions based on health status and metrics"""
    predictions = []
    
    # Always generate at least one prediction for demonstration
    if health_status == HealthStatus.CRITICAL:
        # Critical players get multiple high-probability predictions
        predictions.append(FailurePrediction(
            next_failure_week=random.randint(1, 3),
            failure_probability=round(random.uniform(0.7, 0.9), 2),
            failure_type="balance_depletion",
            failure_reason="Critical risk score indicates imminent economic failure"
        ))
        
        if metrics.inflation_rate > 0.03:
            predictions.append(FailurePrediction(
                next_failure_week=random.randint(2, 4),
                failure_probability=round(random.uniform(0.6, 0.8), 2),
                failure_type="inflation_crisis",
                failure_reason="High inflation rate threatens economic stability"
            ))
    
    elif health_status == HealthStatus.AT_RISK:
        # At-risk players get moderate predictions
        predictions.append(FailurePrediction(
            next_failure_week=random.randint(3, 6),
            failure_probability=round(random.uniform(0.4, 0.7), 2),
            failure_type="balance_depletion",
            failure_reason="Declining balance trend suggests future economic stress"
        ))
        
        if metrics.resource_scarcity > 0.25:
            predictions.append(FailurePrediction(
                next_failure_week=random.randint(4, 8),
                failure_probability=round(random.uniform(0.3, 0.6), 2),
                failure_type="resource_scarcity",
                failure_reason="Resource scarcity may lead to economic constraints"
            ))
    
    else:  # HEALTHY
        # Even healthy players get some low-probability predictions for monitoring
        if random.random() < 0.6:  # 60% chance of getting a prediction
            predictions.append(FailurePrediction(
                next_failure_week=random.randint(6, 12),
                failure_probability=round(random.uniform(0.1, 0.4), 2),
                failure_type="balance_depletion",
                failure_reason="Long-term monitoring suggests potential future risks"
            ))
        
        if metrics.inflation_rate > 0.025 and random.random() < 0.4:
            predictions.append(FailurePrediction(
                next_failure_week=random.randint(8, 12),
                failure_probability=round(random.uniform(0.2, 0.5), 2),
                failure_type="inflation_crisis",
                failure_reason="Moderate inflation may escalate without intervention"
            ))
    
    return predictions

def generate_mitigation_suggestions(health_status: str, metrics: EconomicMetrics, predictions: List[FailurePrediction]) -> List[MitigationSuggestion]:
    """Generate mitigation suggestions based on health status and predictions"""
    suggestions = []
    
    # Always provide some suggestions for demonstration
    if health_status == HealthStatus.CRITICAL:
        suggestions.append(MitigationSuggestion(
            suggestion_id="emergency_intervention_001",
            category="balance",
            priority="critical",
            description="Implement emergency economic intervention measures immediately",
            expected_impact="Prevent economic collapse and stabilize critical metrics",
            implementation_difficulty="high"
        ))
        
        suggestions.append(MitigationSuggestion(
            suggestion_id="expense_reduction_001",
            category="expense",
            priority="critical",
            description="Drastically reduce all non-essential expenses",
            expected_impact="Reduce economic pressure by 40-60%",
            implementation_difficulty="medium"
        ))
    
    elif health_status == HealthStatus.AT_RISK:
        suggestions.append(MitigationSuggestion(
            suggestion_id="balance_stabilization_001",
            category="balance",
            priority="high",
            description="Implement measures to stabilize declining balance trend",
            expected_impact="Reverse negative balance trend within 2-3 weeks",
            implementation_difficulty="medium"
        ))
        
        suggestions.append(MitigationSuggestion(
            suggestion_id="income_boost_001",
            category="income",
            priority="high",
            description="Increase income sources or boost existing income rates",
            expected_impact="Increase daily income by 25-40%",
            implementation_difficulty="low"
        ))
    
    else:  # HEALTHY
        suggestions.append(MitigationSuggestion(
            suggestion_id="preventive_monitoring_001",
            category="monitoring",
            priority="medium",
            description="Implement enhanced monitoring to detect early warning signs",
            expected_impact="Early detection of potential issues",
            implementation_difficulty="low"
        ))
        
        suggestions.append(MitigationSuggestion(
            suggestion_id="optimization_001",
            category="income",
            priority="low",
            description="Optimize existing income streams for better efficiency",
            expected_impact="Improve income efficiency by 10-15%",
            implementation_difficulty="low"
        ))
    
    # Add specific suggestions based on metrics
    if metrics.inflation_rate > 0.03:
        suggestions.append(MitigationSuggestion(
            suggestion_id="inflation_control_001",
            category="expense",
            priority="high",
            description="Implement inflation control measures",
            expected_impact="Reduce inflation rate by 20-30%",
            implementation_difficulty="medium"
        ))
    
    if metrics.resource_scarcity > 0.25:
        suggestions.append(MitigationSuggestion(
            suggestion_id="resource_management_001",
            category="income",
            priority="medium",
            description="Improve resource management and generation",
            expected_impact="Reduce scarcity by 25-40%",
            implementation_difficulty="low"
        ))
    
    if metrics.transaction_velocity < 2:
        suggestions.append(MitigationSuggestion(
            suggestion_id="activity_boost_001",
            category="income",
            priority="medium",
            description="Encourage more frequent economic activity",
            expected_impact="Increase transaction velocity by 50%",
            implementation_difficulty="low"
        ))
    
    # Add suggestions based on failure predictions
    for prediction in predictions:
        if prediction.failure_type == "balance_depletion":
            suggestions.append(MitigationSuggestion(
                suggestion_id="balance_protection_001",
                category="balance",
                priority="high",
                description="Implement balance protection measures",
                expected_impact="Prevent balance depletion",
                implementation_difficulty="medium"
            ))
        
        elif prediction.failure_type == "inflation_crisis":
            suggestions.append(MitigationSuggestion(
                suggestion_id="inflation_prevention_001",
                category="expense",
                priority="high",
                description="Prevent inflation crisis through expense management",
                expected_impact="Avoid inflation crisis",
                implementation_difficulty="high"
            ))
    
    return suggestions