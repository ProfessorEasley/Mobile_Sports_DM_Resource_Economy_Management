import json
import os
import shutil
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import copy
from pathlib import Path

class GameStateManager:
    """
    Manages game state persistence and rollback functionality.
    
    Architecture:
    1. MAIN SAVE FILE: 'game_state.json' - Current game state
    2. BACKUP SAVES: 'game_state_backup_[timestamp].json' - Before each transaction
    3. TRANSACTION LOG: 'transaction_log.json' - All transactions history
    4. CHECKPOINT SAVES: 'checkpoint_[week].json' - Weekly checkpoints
    """
    
    def __init__(self, save_directory: str = "game_saves"):
        self.save_dir = save_directory
        self.main_save_file = os.path.join(save_directory, "game_state.json")
        self.transaction_log_file = os.path.join(save_directory, "transaction_log.json")
        self.backup_dir = os.path.join(save_directory, "backups")
        self.checkpoint_dir = os.path.join(save_directory, "checkpoints")
        
        self._initialize_directories()
        
        self.rollback_stack = []
        self.max_rollback_states = 10
        
    def _initialize_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.save_dir, self.backup_dir, self.checkpoint_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def save_game_state(self, game_state: dict, create_backup: bool = True) -> bool:
        """
        Save the current game state to file.
        
        Args:
            game_state: Complete game state dictionary
            create_backup: Whether to create a backup before saving
        
        Returns:
            Success status
        """
        try:
            # Create backup if requested
            if create_backup and os.path.exists(self.main_save_file):
                self._create_backup()
            
            # Save current state
            with open(self.main_save_file, 'w') as f:
                json.dump(game_state, f, indent=2, default=str)
            
            print(f"✅ Game state saved to {self.main_save_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving game state: {e}")
            return False
    
    def load_game_state(self) -> Optional[dict]:
        """Load the current game state from file"""
        try:
            if not os.path.exists(self.main_save_file):
                print("📝 No save file found, starting fresh")
                return None
            
            with open(self.main_save_file, 'r') as f:
                game_state = json.load(f)
            
            print(f"✅ Game state loaded from {self.main_save_file}")
            return game_state
            
        except Exception as e:
            print(f"❌ Error loading game state: {e}")
            return None
    
    def _create_backup(self):
        """Create a backup of the current save file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"game_state_backup_{timestamp}.json")
        
        try:
            shutil.copy2(self.main_save_file, backup_file)
            
            # Add to rollback stack
            self.rollback_stack.append(backup_file)
            if len(self.rollback_stack) > self.max_rollback_states:
                # Remove oldest backup
                old_backup = self.rollback_stack.pop(0)
                if os.path.exists(old_backup):
                    os.remove(old_backup)
            
            print(f"📦 Backup created: {backup_file}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create backup: {e}")
    
    def rollback_to_previous_state(self) -> bool:
        """Rollback to the previous game state"""
        if not self.rollback_stack:
            print("❌ No previous states available for rollback")
            return False
        
        try:
            backup_file = self.rollback_stack.pop()
            
            shutil.copy2(backup_file, self.main_save_file)
            
            os.remove(backup_file)
            
            print(f"✅ Rolled back to previous state")
            return True
            
        except Exception as e:
            print(f"❌ Error during rollback: {e}")
            return False
    
    def create_checkpoint(self, checkpoint_name: str, game_state: dict) -> bool:
        """Create a named checkpoint save"""
        try:
            checkpoint_file = os.path.join(self.checkpoint_dir, f"checkpoint_{checkpoint_name}.json")
            
            with open(checkpoint_file, 'w') as f:
                json.dump(game_state, f, indent=2, default=str)
            
            print(f"💾 Checkpoint created: {checkpoint_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating checkpoint: {e}")
            return False
    
    def load_checkpoint(self, checkpoint_name: str) -> Optional[dict]:
        """Load a specific checkpoint"""
        try:
            checkpoint_file = os.path.join(self.checkpoint_dir, f"checkpoint_{checkpoint_name}.json")
            
            if not os.path.exists(checkpoint_file):
                print(f"❌ Checkpoint '{checkpoint_name}' not found")
                return None
            
            with open(checkpoint_file, 'r') as f:
                game_state = json.load(f)
            
            print(f"✅ Checkpoint '{checkpoint_name}' loaded")
            return game_state
            
        except Exception as e:
            print(f"❌ Error loading checkpoint: {e}")
            return None
    
    def log_transaction(self, transaction_data: dict):
        """Append transaction to the transaction log"""
        try:
            # Load existing log or create new
            if os.path.exists(self.transaction_log_file):
                with open(self.transaction_log_file, 'r') as f:
                    log = json.load(f)
            else:
                log = {"transactions": [], "metadata": {"created": datetime.now().isoformat()}}
            
            log["transactions"].append(transaction_data)
            
            with open(self.transaction_log_file, 'w') as f:
                json.dump(log, f, indent=2, default=str)
                
        except Exception as e:
            print(f"⚠️ Warning: Could not log transaction: {e}")

class IntegratedEconomicSystem:
    """
    Complete economic system with save/load and monitoring integration.
    This combines the logger, wallet system, and monitoring dashboard.
    """
    
    def __init__(self):
        self.state_manager = GameStateManager()
        self.wallets = {}
        self.metrics = {
            "total_transactions": 0,
            "weekly_deltas": {},
            "inflation_rates": {},
            "alerts": []
        }
        
        self.load_game()
    
    def _normalize_player_id(self, player_id: str) -> str:
        """Ensure player IDs conform to UUID string format."""

        try:
            return str(uuid.UUID(str(player_id)))
        except (ValueError, TypeError):
            generated_id = str(uuid.uuid4())
            print(f"⚠️ Provided player_id '{player_id}' invalid; generated {generated_id} instead")
            return generated_id

    def create_player(
        self,
        player_id: str,
        initial_coins: int = 1000,
        initial_gems: int = 50,
        initial_credits: int = 20,
        credits_cap: int = 100,
    ) -> dict:
        """Create a new player with initial resources."""

        normalized_id = self._normalize_player_id(player_id)
        self.wallets[normalized_id] = {
            "player_id": normalized_id,
            "current_balances": {
                "coins": int(initial_coins),
                "gems": int(initial_gems),
                "credits": int(initial_credits),
            },
            "max_capacities": {
                "coins": int(initial_coins) * 10,
                "gems": int(initial_gems) * 10,
                "credits": int(credits_cap),
            },
            "earn_rates": {
                "coins_per_hour": 0,
                "gems_per_day": 0,
                "credits_per_week": 0,
            },
            "created_at": datetime.now().isoformat(),
        }

        print(f"👤 Created player: {normalized_id}")
        self._auto_save()
        return self.wallets[normalized_id]
    
    def process_transaction(
        self,
        player_id: str,
        currency: str,
        amount: int,
        source: str,
        context: dict | None = None,
        allow_rollback: bool = True,
    ) -> bool:
        """
        Process a transaction with automatic save and optional rollback.
        
        Args:
            player_id: Player identifier
            currency: Type of currency
            amount: Amount (positive for earn, negative for spend)
            source: Origin of transaction
            context: Additional context data
            allow_rollback: Whether to create a rollback point

        Returns:
            Success status
        """

        normalized_id = self._normalize_player_id(player_id)
        if normalized_id not in self.wallets:
            print(f"❌ Player {normalized_id} not found")
            return False

        if allow_rollback:
            self.state_manager.save_game_state(self._get_game_state(), create_backup=True)

        wallet = self.wallets[normalized_id]
        balances = wallet["current_balances"]
        currency = currency.lower()
        currency = {
            "soft": "coins",
            "premium": "gems",
            "coachingcredit": "credits",
            "utility": "credits",
        }.get(currency, currency)

        if currency not in balances:
            print(f"❌ Unsupported currency '{currency}' for {normalized_id}")
            self._log_failed_transaction(normalized_id, currency, amount, source, "UnsupportedCurrency")
            return False

        amount = int(amount)
        transaction_type = "earn" if amount > 0 else "spend"
        delta = abs(amount)

        current_balance = int(balances[currency])
        if transaction_type == "spend" and current_balance < delta:
            print(f"❌ Insufficient {currency} for {normalized_id}")
            self._log_failed_transaction(normalized_id, currency, amount, source, "InsufficientFunds")
            return False

        if transaction_type == "earn" and currency == "credits":
            cap = int(wallet["max_capacities"]["credits"])
            potential_balance = current_balance + delta
            if potential_balance > cap:
                delta = max(cap - current_balance, 0)
                if delta == 0:
                    print(f"⚠️ {normalized_id} already at credits cap")
                    return False

        signed_delta = delta if transaction_type == "earn" else -delta
        balances[currency] = current_balance + signed_delta

        transaction_data = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "player_id": normalized_id,
            "currency": currency,
            "type": transaction_type,
            "amount": signed_delta,
            "source": source,
            "context": context or {},
            "new_balance": int(balances[currency]),
        }

        self.state_manager.log_transaction(transaction_data)
        self.metrics["total_transactions"] += 1

        print(f"✅ {transaction_type.upper()}: {normalized_id} - {abs(signed_delta)} {currency} ({source})")
        print(f"   New balance: {balances[currency]}")

        self._auto_save()

        return True

    def rollback_last_transaction(self) -> bool:
        """Rollback the last transaction"""
        if self.state_manager.rollback_to_previous_state():
            self.load_game()
            return True
        return False
    
    def _log_failed_transaction(self, player_id: str, currency: str, amount: int, source: str, reason: str):
        """Log a failed transaction attempt"""
        transaction_data = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "player_id": player_id,
            "currency": currency,
            "type": "failed",
            "amount": int(amount),
            "source": source,
            "context": {"failure_reason": reason}
        }
        self.state_manager.log_transaction(transaction_data)

    def _get_game_state(self) -> dict:
        """Get the complete game state for saving"""
        return {
            "wallets": self.wallets,
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }

    def _auto_save(self):
        """Automatically save the game state"""
        self.state_manager.save_game_state(self._get_game_state(), create_backup=False)
    
    def save_game(self, create_checkpoint: bool = False, checkpoint_name: str = None):
        """Manually save the game"""
        game_state = self._get_game_state()
        

        self.state_manager.save_game_state(game_state, create_backup=True)
        
        if create_checkpoint and checkpoint_name:
            self.state_manager.create_checkpoint(checkpoint_name, game_state)
    
    def load_game(self) -> bool:
        """Load the game from save file"""
        game_state = self.state_manager.load_game_state()
        
        if game_state:
            self.wallets = game_state.get("wallets", {})
            self.metrics = game_state.get("metrics", {
                "total_transactions": 0,
                "weekly_deltas": {},
                "inflation_rates": {},
                "alerts": []
            })
            print(f"📂 Loaded {len(self.wallets)} players")
            return True
        
        return False
    
    def get_player_balance(self, player_id: str) -> dict:
        """Get all balances for a player"""
        normalized_id = self._normalize_player_id(player_id)
        if normalized_id not in self.wallets:
            return {}
        return copy.deepcopy(self.wallets[normalized_id])

    def get_all_players(self) -> list:
        """Get list of all player IDs"""
        return list(self.wallets.keys())
    
    def print_economy_summary(self):
        """Print a summary of the current economy"""
        print("\n" + "="*60)
        print("ECONOMY SUMMARY")
        print("="*60)
        
        if not self.wallets:
            print("No players in the economy")
            return
        
        totals = {"coins": 0, "gems": 0, "credits": 0}
        for player_data in self.wallets.values():
            balances = player_data.get("current_balances", {})
            for currency in totals:
                totals[currency] += balances.get(currency, 0)

        print(f"\n📊 Total Players: {len(self.wallets)}")
        print(f"📈 Total Transactions: {self.metrics['total_transactions']}")

        print("\n💰 Currency Totals:")
        for currency, total in totals.items():
            avg = total / len(self.wallets) if self.wallets else 0
            print(f"  {currency}: {int(total)} (avg: {avg:.1f})")

        print("\n👥 Player Balances:")
        for player_id in list(self.wallets.keys())[:5]:
            balances = self.wallets[player_id]["current_balances"]
            print(f"  {player_id}:")
            for currency in ["coins", "gems", "credits"]:
                print(f"    {currency}: {balances.get(currency, 0)}")
        
        if len(self.wallets) > 5:
            print(f"  ... and {len(self.wallets) - 5} more players")


def run_example_scenario():
    """Run an example scenario demonstrating all features"""
    
    print("\n" + "="*80)
    print(" "*25 + "ECONOMIC SYSTEM DEMO")
    print(" "*20 + "Save/Load & Rollback Features")
    print("="*80)
    
    game = IntegratedEconomicSystem()
    
    # Scenario 1: Create players
    print("\n📌 SCENARIO 1: Creating Players")
    print("-"*40)
    
    player_1 = str(uuid.uuid4())
    player_2 = str(uuid.uuid4())
    player_3 = str(uuid.uuid4())

    game.create_player(player_1, initial_coins=1000, initial_gems=50, initial_credits=25)
    game.create_player(player_2, initial_coins=1500, initial_gems=75, initial_credits=30)
    game.create_player(player_3, initial_coins=800, initial_gems=30, initial_credits=15)
    
    # Scenario 2: Process transactions
    print("\n📌 SCENARIO 2: Processing Transactions")
    print("-"*40)
    
    game.process_transaction(player_1, "coins", 100, "daily_login_bonus")
    game.process_transaction(player_2, "coins", 100, "daily_login_bonus")

    game.process_transaction(
        player_1,
        "gems",
        -10,
        "cosmetic_purchase",
        {"item": "Golden Hat"},
    )

    game.process_transaction(
        player_2,
        "coins",
        250,
        "quest_completion",
        {"quest_id": "main_quest_01"},
    )
    
    game.save_game(create_checkpoint=True, checkpoint_name="week_1")
    
    # Scenario 3: Failed transaction
    print("\n📌 SCENARIO 3: Failed Transaction (Insufficient Funds)")
    print("-"*40)
    
    success = game.process_transaction(player_3, "gems", -100, "expensive_item")
    if not success:
        print("  Transaction failed as expected")
    
    # Scenario 4: Coaching credit cap
    print("\n📌 SCENARIO 4: Coaching Credit Cap")
    print("-"*40)
    
    game.process_transaction(player_1, "credits", 50, "achievement_reward")
    game.process_transaction(player_1, "credits", 60, "bonus_reward")
    
    game.print_economy_summary()
    
    # Scenario 5: Rollback demonstration
    print("\n📌 SCENARIO 5: Rollback Demonstration")
    print("-"*40)
    
    print("\n🎯 Making a large transaction...")
    game.process_transaction(player_2, "coins", -1000, "major_purchase")
    
    print("\n🔄 Rolling back the transaction...")
    if game.rollback_last_transaction():
        print("  Rollback successful!")
        restored = game.get_player_balance(player_2)["current_balances"]["coins"]
        print(f"  Player 2 balance restored: {restored}")
    
    # Scenario 6: Save and reload
    print("\n📌 SCENARIO 6: Save and Reload")
    print("-"*40)
    
    print("\n💾 Saving game...")
    game.save_game()
    
    print("\n🔄 Creating new game instance and loading...")
    new_game = IntegratedEconomicSystem()
    
    print(f"\n✅ Loaded players: {new_game.get_all_players()}")
    
    new_game.print_economy_summary()
    
    print("\n" + "="*80)
    print(" "*30 + "DEMO COMPLETE")
    print("="*80)
    
    return new_game


def main():
    """Main entry point"""
    
    print("\n" + "="*80)
    print(" "*20 + "PHASE 3 ECONOMIC SYSTEM")
    print(" "*15 + "Complete Implementation with Save/Load")
    print("="*80)
    
    print("\n🎮 STARTING ECONOMIC SYSTEM...")
    print("\nThis system includes:")
    print("  ✅ Automatic saving after each transaction")
    print("  ✅ Rollback capability for last 10 transactions")
    print("  ✅ Checkpoint saves for important milestones")
    print("  ✅ Complete transaction logging")
    print("  ✅ Player wallet management")
    print("  ✅ Economic metrics tracking")
    
    game = run_example_scenario()
    
    print("\n📁 FILE STRUCTURE CREATED:")
    print("game_saves/")
    print("├── game_state.json          # Current game state")
    print("├── transaction_log.json     # All transactions")
    print("├── backups/                 # Automatic backups")
    print("│   └── game_state_backup_*.json")
    print("└── checkpoints/             # Manual checkpoints")
    print("    └── checkpoint_*.json")
    
    print("\n✅ System ready for production use!")
    print("\n💡 TIP: Run 'python complete_economic_system.py' to execute")
    
    return game


if __name__ == "__main__":
    game_instance = main()
