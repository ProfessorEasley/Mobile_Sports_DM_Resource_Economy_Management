from typing import Dict, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

class WalletState(BaseModel):
    """Current wallet state for simulation"""
    coins: int = Field(ge=0, description="Current coin balance")
    gems: int = Field(ge=0, description="Current gem balance") 
    credits: int = Field(ge=0, description="Current credit balance")

class SimulationParameters(BaseModel):
    """Parameters for wallet simulation"""
    daily_income_coins: int = Field(default=100, ge=0, description="Daily coin income")
    daily_income_gems: int = Field(default=2, ge=0, description="Daily gem income")
    daily_expenses_coins: int = Field(default=50, ge=0, description="Daily coin expenses")
    weekly_bonus_coins: int = Field(default=200, ge=0, description="Weekly bonus coins")
    weekly_bonus_gems: int = Field(default=10, ge=0, description="Weekly bonus gems")
    special_events: Dict[str, int] = Field(default_factory=dict, description="Special event modifiers")

class WalletSimulationRequest(BaseModel):
    """Request model for wallet simulation"""
    player_id: UUID
    current_wallet: WalletState
    simulation_params: SimulationParameters
    include_transactions: bool = Field(default=True, description="Include transaction details")

class TransactionSimulation(BaseModel):
    """Individual transaction simulation"""
    day: int = Field(ge=1, le=7, description="Day of week (1-7)")
    transaction_type: str = Field(description="Type of transaction")
    currency: str = Field(description="Currency affected")
    amount: int = Field(description="Amount (positive for income, negative for expense)")
    balance_after: int = Field(description="Balance after transaction")

class WalletSimulationResponse(BaseModel):
    """Response model for wallet simulation"""
    player_id: UUID
    simulation_week: int = Field(default=1, description="Simulated week number")
    initial_wallet: WalletState
    final_wallet: WalletState
    net_changes: WalletState
    transactions: list[TransactionSimulation] = Field(default_factory=list)
    simulation_summary: Dict[str, Any] = Field(default_factory=dict)
    alerts: list[str] = Field(default_factory=list)
