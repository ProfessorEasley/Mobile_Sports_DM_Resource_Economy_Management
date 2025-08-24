from datetime import datetime
import uuid
import json
import copy 

def log_transaction(
    player_id: str,
    currency_type: str, 
    amount: float,      
    transaction_type: str, 
    source_sink: str,  
    context_data: dict  
):
    """
    Logs a single economic transaction to the console using a unified format.
    """
    try:
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        if not isinstance(context_data, dict):
            print(f"Warning: context_data must be a dictionary. Received: {type(context_data)}. Converting to empty dict.")
            context_data = {}

        transaction_record = {
            "transaction_id": transaction_id,
            "timestamp": timestamp,
            "player_id": player_id,
            "currency_type": currency_type,
            "amount": amount,
            "transaction_type": transaction_type,
            "source_sink": source_sink,
            "context_data": context_data,
        }

        print(f"\n--- Logged Transaction: {transaction_id} ---")
        print(json.dumps(transaction_record, indent=2))
        print("--------------------------------------")

    except Exception as e:
        print(f"Error logging transaction: {e}")

class PlayerWallet:
    """
    A simplified PlayerWallet class to simulate currency balances.
    In a real system, this would interact with a database.
    """
    def __init__(self, player_id: str, initial_soft: float = 0.0, initial_premium: float = 0.0,
                 initial_utility: float = 0.0, initial_coaching_credits: float = 0.0,
                 coaching_credit_cap: float = 100.0):
        self.player_id = player_id
        self.balances = {
            "Soft": initial_soft,
            "Premium": initial_premium,
            "Utility": initial_utility,
            "CoachingCredit": initial_coaching_credits
        }
        self.coaching_credit_cap = coaching_credit_cap
        print(f"Wallet initialized for {self.player_id}: {self.balances}")

    def get_balance(self, currency_type: str) -> float:
        """Returns the current balance for a given currency type."""
        return self.balances.get(currency_type, 0.0)

    def add_currency(self, currency_type: str, amount: float, source_sink: str, context_data: dict = None):
        """Adds currency to the wallet and logs the transaction."""
        if amount <= 0:
            print(f"Error: Amount to add must be positive. Received {amount}")
            return False

        if currency_type == "CoachingCredit":
            new_amount = self.balances["CoachingCredit"] + amount
            if new_amount > self.coaching_credit_cap:
                excess_amount = new_amount - self.coaching_credit_cap
                self.balances["CoachingCredit"] = self.coaching_credit_cap
                log_transaction(
                    player_id=self.player_id,
                    currency_type=currency_type,
                    amount=amount - excess_amount, 
                    transaction_type="Earn",
                    source_sink=source_sink,
                    context_data={**(context_data or {}), "cap_reached": True, "excess_amount_discarded": excess_amount}
                )
                print(f"Coaching credits capped for {self.player_id}. Added {amount - excess_amount}, {excess_amount} discarded.")
                return True
            else:
                self.balances[currency_type] += amount
                log_transaction(
                    player_id=self.player_id,
                    currency_type=currency_type,
                    amount=amount,
                    transaction_type="Earn",
                    source_sink=source_sink,
                    context_data=context_data
                )
                print(f"Added {amount} {currency_type} to {self.player_id}. New balance: {self.get_balance(currency_type)}")
                return True
        else:
            self.balances[currency_type] += amount
            log_transaction(
                player_id=self.player_id,
                currency_type=currency_type,
                amount=amount,
                transaction_type="Earn",
                source_sink=source_sink,
                context_data=context_data
            )
            print(f"Added {amount} {currency_type} to {self.player_id}. New balance: {self.get_balance(currency_type)}")
            return True


    def spend_currency(self, currency_type: str, amount: float, source_sink: str, context_data: dict = None) -> bool:
        """Spends currency from the wallet and logs the transaction."""
        if amount <= 0:
            print(f"Error: Amount to spend must be positive. Received {amount}")
            return False
        if self.balances.get(currency_type, 0) < amount:
            print(f"Error: Insufficient {currency_type} for {self.player_id}. Needed {amount}, has {self.get_balance(currency_type)}")
            log_transaction(
                player_id=self.player_id,
                currency_type=currency_type,
                amount=-amount,
                transaction_type="Spend",
                source_sink=f"{source_sink}_Failed",
                context_data={**(context_data or {}), "status": "Failed", "reason": "InsufficientFunds"}
            )
            return False

        self.balances[currency_type] -= amount
        log_transaction(
            player_id=self.player_id,
            currency_type=currency_type,
            amount=-amount,
            transaction_type="Spend",
            source_sink=source_sink,
            context_data=context_data
        )
        print(f"Spent {amount} {currency_type} from {self.player_id}. New balance: {self.get_balance(currency_type)}")
        return True

def simulate_transaction_with_rollback(wallet: PlayerWallet, currency_type: str, amount: float,
                                       source_sink: str, context_data: dict = None,
                                       simulate_failure: bool = False):
    """
    Simulates a transaction and demonstrates rollback logic if it fails.
    In a real system, this would involve database transactions.
    """
    print(f"\n--- Simulating Transaction for {wallet.player_id}: {source_sink} ---")
    initial_balances = copy.deepcopy(wallet.balances) 

    transaction_successful = False
    if amount > 0:
        transaction_successful = wallet.add_currency(currency_type, amount, source_sink, context_data)
    else:
        transaction_successful = wallet.spend_currency(currency_type, abs(amount), source_sink, context_data)

    if simulate_failure or not transaction_successful:
        print(f"Transaction for {wallet.player_id} failed. Initiating rollback.")
        wallet.balances = initial_balances
        log_transaction(
            player_id=wallet.player_id,
            currency_type=currency_type,
            amount=amount,
            transaction_type="Rollback",
            source_sink="TransactionFailed",
            context_data={
                **(context_data or {}),
                "original_source_sink": source_sink,
                "reason": "SimulatedFailure" if simulate_failure else "InsufficientFunds",
                "reverted_to_balance": wallet.balances.get(currency_type)
            }
        )
        print(f"Wallet for {wallet.player_id} rolled back. Current balance: {wallet.get_balance(currency_type)}")
        return False
    else:
        print(f"Transaction for {wallet.player_id} completed successfully.")
        return True

def run_integration_test_cases():
    """
    Runs a series of integration test cases for wallet operations,
    coaching credit logic, and rollback.
    """
    print("\n--- Running Integration Test Cases ---")

    player1 = PlayerWallet("player_Alice", initial_soft=1000, initial_premium=50, initial_coaching_credits=80)
    player2 = PlayerWallet("player_Bob", initial_soft=500, initial_premium=10, initial_utility=5, coaching_credit_cap=50)

    # Test Case 1: Basic Earn - Soft Currency
    print("\nTest Case 1: Basic Earn - Soft Currency")
    player1.add_currency("Soft", 200, "DailyLoginBonus", {"day": 1})
    assert player1.get_balance("Soft") == 1200

    # Test Case 2: Basic Spend - Premium Currency
    print("\nTest Case 2: Basic Spend - Premium Currency")
    player1.spend_currency("Premium", 10, "CosmeticPurchase", {"item_id": "Hat_001"})
    assert player1.get_balance("Premium") == 40

    # Test Case 3: Insufficient Funds - Soft Currency
    print("\nTest Case 3: Insufficient Funds - Soft Currency")
    player2.spend_currency("Soft", 1000, "PlayerUpgrade", {"player_id": "P_001"})
    assert player2.get_balance("Soft") == 500 

    # Test Case 4: Coaching Credit Earn - Below Cap
    print("\nTest Case 4: Coaching Credit Earn - Below Cap")
    player2.add_currency("CoachingCredit", 20, "WeeklyChallengeReward", {"challenge": "SprintDrill"})
    assert player2.get_balance("CoachingCredit") == 20 

    # Test Case 5: Coaching Credit Earn - Hitting Cap
    print("\nTest Case 5: Coaching Credit Earn - Hitting Cap")
    player2.add_currency("CoachingCredit", 40, "SeasonReward", {"season": 1}) 
    assert player2.get_balance("CoachingCredit") == 50

    # Test Case 6: Coaching Credit Earn - Exceeding Cap (with discard)
    print("\nTest Case 6: Coaching Credit Earn - Exceeding Cap (with discard)")
    player2.add_currency("CoachingCredit", 30, "EventBonus", {"event": "HolidayCup"}) 
    assert player2.get_balance("CoachingCredit") == 50

    # Test Case 7: Utility Currency Usage
    print("\nTest Case 7: Utility Currency Usage")
    player2.spend_currency("Utility", 1, "MatchBoosterUse", {"booster_type": "SpeedBoost"})
    assert player2.get_balance("Utility") == 4

    # Test Case 8: Rollback Simulation - Successful Transaction
    print("\nTest Case 8: Rollback Simulation - Successful Transaction")
    simulate_transaction_with_rollback(player1, "Soft", 50, "QuestCompletion", {"quest_id": "Q_Daily"})
    assert player1.get_balance("Soft") == 1250

    # Test Case 9: Rollback Simulation - Simulated Failure
    print("\nTest Case 9: Rollback Simulation - Simulated Failure (Spend)")
    initial_soft_p1 = player1.get_balance("Soft")
    simulate_transaction_with_rollback(player1, "Soft", -100, "ItemCrafting", {"item_name": "MegaPotion"}, simulate_failure=True)
    assert player1.get_balance("Soft") == initial_soft_p1 

    # Test Case 10: Rollback Simulation - Insufficient Funds (Spend)
    print("\nTest Case 10: Rollback Simulation - Insufficient Funds (Spend)")
    initial_premium_p2 = player2.get_balance("Premium")
    simulate_transaction_with_rollback(player2, "Premium", -100, "ExclusiveOffer")
    assert player2.get_balance("Premium") == initial_premium_p2 

    print("\n--- All Integration Test Cases Completed ---")


if __name__ == "__main__":
    run_integration_test_cases()
