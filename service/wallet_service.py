from models.wallet_models import WalletSimulationRequest, WalletSimulationResponse, TransactionSimulation
from processors.wallet_simulation_processor import simulate_wallet_week, evaluate_wallet_risks

def run_wallet_simulation(request: WalletSimulationRequest) -> WalletSimulationResponse:
    """
    Main service function for wallet simulation
    Orchestrates the simulation process and returns formatted response
    """
    # Run the simulation
    simulation_result = simulate_wallet_week(request)
    
    # Evaluate risks
    alerts = evaluate_wallet_risks(simulation_result)
    
    # Convert transactions to proper format
    transactions = [
        TransactionSimulation(**tx) for tx in simulation_result["transactions"]
    ] if request.include_transactions else []
    
    # Build response
    return WalletSimulationResponse(
        player_id=request.player_id,
        simulation_week=1,
        initial_wallet=request.current_wallet,
        final_wallet=simulation_result["final_wallet"],
        net_changes=simulation_result["net_changes"],
        transactions=transactions,
        simulation_summary=simulation_result["summary"],
        alerts=alerts
    )

