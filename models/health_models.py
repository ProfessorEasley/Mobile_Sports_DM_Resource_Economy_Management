from typing import Dict, List, Optional, ClassVar
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

class HealthStatus(BaseModel):
    """Health status levels for economy monitoring"""
    HEALTHY: ClassVar[str] = "healthy"
    AT_RISK: ClassVar[str] = "at_risk"
    CRITICAL: ClassVar[str] = "critical"

class HealthMonitoringRequest(BaseModel):
    """Request model for economy health monitoring"""
    player_id: UUID = Field(description="Player ID for health analysis")
    analysis_period_weeks: int = Field(default=4, ge=1, le=12, description="Number of weeks to analyze")
    include_predictions: bool = Field(default=True, description="Include failure predictions")
    include_suggestions: bool = Field(default=True, description="Include mitigation suggestions")

class FailurePrediction(BaseModel):
    """Prediction of potential financial failure"""
    next_failure_week: int = Field(ge=0, description="Week number when failure is predicted")
    failure_probability: float = Field(ge=0.0, le=1.0, description="Probability of failure (0.0-1.0)")
    failure_type: str = Field(description="Type of predicted failure")
    failure_reason: str = Field(description="Reason for predicted failure")

class MitigationSuggestion(BaseModel):
    """Suggestion for mitigating economic risks"""
    suggestion_id: str = Field(description="Unique identifier for the suggestion")
    category: str = Field(description="Category of suggestion (income, expense, balance)")
    priority: str = Field(description="Priority level (low, medium, high, critical)")
    description: str = Field(description="Detailed suggestion description")
    expected_impact: str = Field(description="Expected impact of implementing suggestion")
    implementation_difficulty: str = Field(description="Difficulty of implementation")

class EconomicMetrics(BaseModel):
    """Economic metrics for health analysis"""
    inflation_rate: float = Field(ge=0.0, description="Current inflation rate")
    resource_scarcity: float = Field(ge=0.0, le=1.0, description="Resource scarcity level")
    balance_trend: str = Field(description="Balance trend (increasing, stable, decreasing)")
    transaction_velocity: float = Field(ge=0.0, description="Transactions per day")
    risk_score: float = Field(ge=0.0, le=100.0, description="Overall risk score (0-100)")

class HealthMonitoringResponse(BaseModel):
    """Response model for economy health monitoring"""
    player_id: UUID
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    health_status: str = Field(description="Current health status")
    economic_metrics: EconomicMetrics
    failure_predictions: List[FailurePrediction] = Field(default_factory=list)
    mitigation_suggestions: List[MitigationSuggestion] = Field(default_factory=list)
    analysis_period_weeks: int
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in analysis")
    next_analysis_due: datetime = Field(description="When next analysis should be performed")

class HealthLogEntry(BaseModel):
    """Database entry for economy health logs"""
    log_id: str = Field(description="Unique log entry identifier")
    player_id: UUID
    analysis_timestamp: datetime
    health_status: str
    economic_metrics: EconomicMetrics
    failure_predictions: List[FailurePrediction]
    mitigation_suggestions: List[MitigationSuggestion]
    confidence_score: float
    analysis_period_weeks: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
