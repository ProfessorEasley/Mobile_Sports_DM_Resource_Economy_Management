from fastapi import APIRouter
from models.wallet_models import WalletSimulationRequest, WalletSimulationResponse
from models.health_models import HealthMonitoringRequest, HealthMonitoringResponse
from service.wallet_service import run_wallet_simulation
from service.health_service import HealthMonitoringService

router = APIRouter()
health_service = HealthMonitoringService()

@router.post("/wallet/simulate", response_model=WalletSimulationResponse)
def simulate_wallet(data: WalletSimulationRequest):
    """
    Simulate one week of wallet transactions

    This endpoint simulates how a player's wallet would change over one week
    based on daily income, expenses, bonuses, and special events.
    """
    return run_wallet_simulation(data)

@router.get("/wallet/health", response_model=HealthMonitoringResponse)
def get_economy_health(player_id: str, analysis_period_weeks: int = 4, include_predictions: bool = True, include_suggestions: bool = True):
    """
    Get economy health status and failure predictions
    
    This endpoint analyzes a player's economic health, predicts potential failures,
    and provides mitigation suggestions based on historical data.
    """
    request = HealthMonitoringRequest(
        player_id=player_id,
        analysis_period_weeks=analysis_period_weeks,
        include_predictions=include_predictions,
        include_suggestions=include_suggestions
    )
    return health_service.analyze_player_health(request)

@router.get("/wallet/health/history")
def get_health_history(player_id: str, limit: int = 10):
    """
    Get health analysis history for a player
    """
    return health_service.get_player_health_history(player_id, limit)

@router.get("/wallet/health/summary")
def get_health_summary(player_id: str):
    """
    Get a summary of the player's current health status
    """
    return health_service.get_health_summary(player_id)

# Browser-friendly GET endpoints for easy testing
@router.get("/wallet/simulate/browser")
def simulate_wallet_browser(
    player_id: str = "123e4567-e89b-12d3-a456-426614174000",
    initial_coins: int = 1000,
    initial_gems: int = 50,
    initial_credits: int = 25,
    daily_income_coins: int = 100,
    daily_income_gems: int = 2,
    daily_expenses_coins: int = 50,
    weekly_bonus_coins: int = 200,
    weekly_bonus_gems: int = 10
):
    """
    Browser-friendly wallet simulation endpoint
    
    This endpoint allows you to test wallet simulation directly in the browser
    by passing parameters as query parameters instead of JSON body.
    """
    from models.wallet_models import WalletSimulationRequest, WalletState, SimulationParameters
    
    request = WalletSimulationRequest(
        player_id=player_id,
        current_wallet=WalletState(
            coins=initial_coins,
            gems=initial_gems,
            credits=initial_credits
        ),
        simulation_params=SimulationParameters(
            daily_income_coins=daily_income_coins,
            daily_income_gems=daily_income_gems,
            daily_expenses_coins=daily_expenses_coins,
            weekly_bonus_coins=weekly_bonus_coins,
            weekly_bonus_gems=weekly_bonus_gems,
            special_events={}
        ),
        include_transactions=True
    )
    
    return run_wallet_simulation(request)

