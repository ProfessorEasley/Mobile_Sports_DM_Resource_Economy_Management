"""
Wallet Simulation Processor
==========================

This module contains the core logic for simulating wallet transactions
over a one-week period, including daily income, expenses, and weekly bonuses.
"""

import random
from typing import Dict, List, Any
from copy import deepcopy
from models.wallet_models import WalletState, SimulationParameters

def simulate_wallet_week(request) -> Dict[str, Any]:
    """
    Simulate a player's wallet over one week
    
    Args:
        request: WalletSimulationRequest containing simulation parameters
        
    Returns:
        Dict containing simulation results
    """
    # Create a copy of the wallet to avoid modifying the original
    wallet = deepcopy(request.current_wallet)
    initial_wallet = deepcopy(request.current_wallet)
    
    transactions = []
    daily_balances = {
        "coins": [wallet.coins],
        "gems": [wallet.gems], 
        "credits": [wallet.credits]
    }
    
    params = request.simulation_params
    
    # Simulate 7 days
    for day in range(1, 8):
        # Daily income
        if params.daily_income_coins > 0:
            wallet.coins += params.daily_income_coins
            transactions.append({
                "day": day,
                "transaction_type": "daily_income",
                "currency": "coins",
                "amount": params.daily_income_coins,
                "balance_after": wallet.coins
            })
        
        if params.daily_income_gems > 0:
            wallet.gems += params.daily_income_gems
            transactions.append({
                "day": day,
                "transaction_type": "daily_income", 
                "currency": "gems",
                "amount": params.daily_income_gems,
                "balance_after": wallet.gems
            })
        
        # Daily expenses
        if params.daily_expenses_coins > 0:
            wallet.coins -= params.daily_expenses_coins
            transactions.append({
                "day": day,
                "transaction_type": "daily_expense",
                "currency": "coins", 
                "amount": -params.daily_expenses_coins,
                "balance_after": wallet.coins
            })
        
        # Weekly bonus on day 7
        if day == 7:
            if params.weekly_bonus_coins > 0:
                wallet.coins += params.weekly_bonus_coins
                transactions.append({
                    "day": day,
                    "transaction_type": "weekly_bonus",
                    "currency": "coins",
                    "amount": params.weekly_bonus_coins,
                    "balance_after": wallet.coins
                })
            
            if params.weekly_bonus_gems > 0:
                wallet.gems += params.weekly_bonus_gems
                transactions.append({
                    "day": day,
                    "transaction_type": "weekly_bonus",
                    "currency": "gems",
                    "amount": params.weekly_bonus_gems,
                    "balance_after": wallet.gems
                })
        
        # Record daily balances
        daily_balances["coins"].append(wallet.coins)
        daily_balances["gems"].append(wallet.gems)
        daily_balances["credits"].append(wallet.credits)
    
    # Calculate net changes
    net_changes = WalletState(
        coins=wallet.coins - initial_wallet.coins,
        gems=wallet.gems - initial_wallet.gems,
        credits=wallet.credits - initial_wallet.credits
    )
    
    # Create summary
    summary = {
        "total_transactions": len(transactions),
        "daily_balances": daily_balances,
        "peak_balance": {
            "coins": max(daily_balances["coins"]),
            "gems": max(daily_balances["gems"]),
            "credits": max(daily_balances["credits"])
        },
        "lowest_balance": {
            "coins": min(daily_balances["coins"]),
            "gems": min(daily_balances["gems"]),
            "credits": min(daily_balances["credits"])
        }
    }
    
    return {
        "final_wallet": wallet,
        "net_changes": net_changes,
        "transactions": transactions,
        "summary": summary
    }

def evaluate_wallet_risks(simulation_result: Dict[str, Any]) -> List[str]:
    """
    Evaluate wallet risks and generate alerts
    
    Args:
        simulation_result: Result from simulate_wallet_week
        
    Returns:
        List of alert messages
    """
    alerts = []
    final_wallet = simulation_result["final_wallet"]
    lowest_balance = simulation_result["summary"]["lowest_balance"]
    
    # Check for low balances
    if lowest_balance["coins"] < 100:
        alerts.append(f"Week simulation: Coin balance dropped to {lowest_balance['coins']} (below 100 threshold)")
    
    if lowest_balance["gems"] < 5:
        alerts.append(f"Week simulation: Gem balance dropped to {lowest_balance['gems']} (below 5 threshold)")
    
    if lowest_balance["credits"] < 10:
        alerts.append(f"Week simulation: Credit balance dropped to {lowest_balance['credits']} (below 10 threshold)")
    
    # Check for negative balances
    if final_wallet.coins < 0:
        alerts.append(f"Week simulation: Coin balance went negative: {final_wallet.coins}")
    
    if final_wallet.gems < 0:
        alerts.append(f"Week simulation: Gem balance went negative: {final_wallet.gems}")
    
    if final_wallet.credits < 0:
        alerts.append(f"Week simulation: Credit balance went negative: {final_wallet.credits}")
    
    return alerts
