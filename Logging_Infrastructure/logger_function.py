from datetime import datetime
import uuid
import json
import copy


def log_transaction(
    player_id: str,
    currency: str,
    amount: int,
    transaction_type: str,
    source: str,
    context: dict | None,
):
    """Logs a single economic transaction to the console using the standardized schema."""

    try:
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        payload = context if isinstance(context, dict) else {}

        transaction_record = {
            "transaction_id": transaction_id,
            "timestamp": timestamp,
            "player_id": player_id,
            "currency": currency.lower(),
            "type": transaction_type.lower(),
            "amount": int(amount),
            "source": source,
            "context": payload,
        }

        print(f"\n--- Logged Transaction: {transaction_id} ---")
        print(json.dumps(transaction_record, indent=2))
        print("--------------------------------------")

    except Exception as exc:
        print(f"Error logging transaction: {exc}")


class PlayerWallet:
    """A simplified PlayerWallet class aligned with the integration schema."""

    SUPPORTED_CURRENCIES = {"coins", "gems", "credits"}
    LEGACY_CURRENCY_MAP = {
        "soft": "coins",
        "premium": "gems",
        "coachingcredit": "credits",
        "utility": "credits",
    }

    def __init__(
        self,
        player_id: str,
        initial_coins: int = 0,
        initial_gems: int = 0,
        initial_credits: int = 0,
        credits_cap: int = 100,
    ):
        self.player_id = self._normalize_player_id(player_id)
        self.balances = {
            "coins": int(initial_coins),
            "gems": int(initial_gems),
            "credits": int(initial_credits),
        }
        self.max_capacities = {
            "coins": int(initial_coins) * 10 or 10000,
            "gems": int(initial_gems) * 10 or 500,
            "credits": int(credits_cap),
        }
        print(f"Wallet initialized for {self.player_id}: {self.balances}")

    @staticmethod
    def _normalize_player_id(player_id: str) -> str:
        try:
            return str(uuid.UUID(str(player_id)))
        except (ValueError, TypeError):
            generated = str(uuid.uuid4())
            print(f"⚠️ Invalid player_id '{player_id}'. Using generated ID {generated}")
            return generated

    def get_balance(self, currency: str) -> int:
        """Return the current balance for a given currency."""

        currency = currency.lower()
        currency = self.LEGACY_CURRENCY_MAP.get(currency, currency)
        return self.balances.get(currency, 0)

    def add_currency(self, currency: str, amount: int, source: str, context: dict | None = None) -> bool:
        """Add currency to the wallet, respecting caps for credits."""

        currency = currency.lower()
        currency = self.LEGACY_CURRENCY_MAP.get(currency, currency)
        amount = int(amount)

        if amount <= 0:
            print(f"Error: Amount to add must be positive. Received {amount}")
            return False
        if currency not in self.SUPPORTED_CURRENCIES:
            print(f"Error: Unsupported currency {currency}")
            return False

        if currency == "credits":
            cap = self.max_capacities["credits"]
            new_amount = self.balances["credits"] + amount
            if new_amount > cap:
                excess = new_amount - cap
                amount -= excess
                self.balances["credits"] = cap
                log_transaction(
                    player_id=self.player_id,
                    currency=currency,
                    amount=amount,
                    transaction_type="earn",
                    source=source,
                    context={**(context or {}), "cap_reached": True, "excess_amount_discarded": excess},
                )
                print(f"Credits capped for {self.player_id}. Added {amount}, discarded {excess}.")
                return True

        self.balances[currency] += amount
        log_transaction(
            player_id=self.player_id,
            currency=currency,
            amount=amount,
            transaction_type="earn",
            source=source,
            context=context,
        )
        print(f"Added {amount} {currency} to {self.player_id}. New balance: {self.get_balance(currency)}")
        return True

    def spend_currency(self, currency: str, amount: int, source: str, context: dict | None = None) -> bool:
        """Spend currency from the wallet and log the transaction."""

        currency = currency.lower()
        currency = self.LEGACY_CURRENCY_MAP.get(currency, currency)
        amount = int(amount)

        if amount <= 0:
            print(f"Error: Amount to spend must be positive. Received {amount}")
            return False
        if currency not in self.SUPPORTED_CURRENCIES:
            print(f"Error: Unsupported currency {currency}")
            return False
        if self.get_balance(currency) < amount:
            print(
                f"Error: Insufficient {currency} for {self.player_id}. Needed {amount}, has {self.get_balance(currency)}"
            )
            log_transaction(
                player_id=self.player_id,
                currency=currency,
                amount=-amount,
                transaction_type="spend",
                source=f"{source}_failed",
                context={**(context or {}), "status": "failed", "reason": "InsufficientFunds"},
            )
            return False

        self.balances[currency] -= amount
        log_transaction(
            player_id=self.player_id,
            currency=currency,
            amount=-amount,
            transaction_type="spend",
            source=source,
            context=context,
        )
        print(f"Spent {amount} {currency} from {self.player_id}. New balance: {self.get_balance(currency)}")
        return True

def simulate_transaction_with_rollback(
    wallet: PlayerWallet,
    currency: str,
    amount: int,
    source: str,
    context: dict | None = None,
    simulate_failure: bool = False,
):
    """Simulate a transaction and demonstrate rollback logic if it fails."""

    print(f"\n--- Simulating Transaction for {wallet.player_id}: {source} ---")
    initial_balances = copy.deepcopy(wallet.balances)

    transaction_successful = False
    if amount > 0:
        transaction_successful = wallet.add_currency(currency, amount, source, context)
    else:
        transaction_successful = wallet.spend_currency(currency, abs(amount), source, context)

    if simulate_failure or not transaction_successful:
        print(f"Transaction for {wallet.player_id} failed. Initiating rollback.")
        wallet.balances = initial_balances
        log_transaction(
            player_id=wallet.player_id,
            currency=currency,
            amount=amount,
            transaction_type="rollback",
            source="transaction_failed",
            context={
                **(context or {}),
                "original_source": source,
                "reason": "SimulatedFailure" if simulate_failure else "InsufficientFunds",
                "reverted_to_balance": wallet.get_balance(currency),
            },
        )
        print(f"Wallet for {wallet.player_id} rolled back. Current balance: {wallet.get_balance(currency)}")
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

    player1 = PlayerWallet(str(uuid.uuid4()), initial_coins=1000, initial_gems=50, initial_credits=80)
    player2 = PlayerWallet(str(uuid.uuid4()), initial_coins=500, initial_gems=10, initial_credits=20, credits_cap=50)

    # Test Case 1: Basic Earn - Coins
    print("\nTest Case 1: Basic Earn - Coins")
    player1.add_currency("coins", 200, "daily_login_bonus", {"day": 1})
    assert player1.get_balance("coins") == 1200

    # Test Case 2: Basic Spend - Gems
    print("\nTest Case 2: Basic Spend - Gems")
    player1.spend_currency("gems", 10, "cosmetic_purchase", {"item_id": "Hat_001"})
    assert player1.get_balance("gems") == 40

    # Test Case 3: Insufficient Funds - Coins
    print("\nTest Case 3: Insufficient Funds - Coins")
    player2.spend_currency("coins", 1000, "player_upgrade", {"player_id": "P_001"})
    assert player2.get_balance("coins") == 500

    # Test Case 4: Credits Earn - Below Cap
    print("\nTest Case 4: Credits Earn - Below Cap")
    player2.add_currency("credits", 20, "weekly_challenge_reward", {"challenge": "SprintDrill"})
    assert player2.get_balance("credits") == 40

    # Test Case 5: Credits Earn - Hitting Cap
    print("\nTest Case 5: Credits Earn - Hitting Cap")
    player2.add_currency("credits", 10, "season_reward", {"season": 1})
    assert player2.get_balance("credits") == 50

    # Test Case 6: Credits Earn - Exceeding Cap (with discard)
    print("\nTest Case 6: Credits Earn - Exceeding Cap (with discard)")
    player2.add_currency("credits", 30, "event_bonus", {"event": "HolidayCup"})
    assert player2.get_balance("credits") == 50

    # Test Case 7: Rollback Simulation - Successful Transaction
    print("\nTest Case 7: Rollback Simulation - Successful Transaction")
    simulate_transaction_with_rollback(player1, "coins", 50, "quest_completion", {"quest_id": "Q_Daily"})
    assert player1.get_balance("coins") == 1250

    # Test Case 8: Rollback Simulation - Simulated Failure
    print("\nTest Case 8: Rollback Simulation - Simulated Failure (Spend)")
    initial_coins_p1 = player1.get_balance("coins")
    simulate_transaction_with_rollback(
        player1,
        "coins",
        -100,
        "item_crafting",
        {"item_name": "MegaPotion"},
        simulate_failure=True,
    )
    assert player1.get_balance("coins") == initial_coins_p1

    # Test Case 9: Rollback Simulation - Insufficient Funds (Spend)
    print("\nTest Case 9: Rollback Simulation - Insufficient Funds (Spend)")
    initial_gems_p2 = player2.get_balance("gems")
    simulate_transaction_with_rollback(player2, "gems", -100, "exclusive_offer")
    assert player2.get_balance("gems") == initial_gems_p2

    print("\n--- All Integration Test Cases Completed ---")

    print("\n--- All Integration Test Cases Completed ---")


if __name__ == "__main__":
    run_integration_test_cases()
