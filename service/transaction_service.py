from uuid import uuid4
from datetime import datetime, timedelta
from typing import List, Optional
from models.transactions_models import TransactionResponse


def get_transaction_history(user_id: str, limit: Optional[int] = 10) -> List[TransactionResponse]:
    """
    Get transaction history for a user with mock data.
    
    Args:
        user_id: User identifier
        limit: Maximum number of transactions to return (default: 10)
    
    Returns:
        List of transaction responses filtered by user_id
    """
    
    # Mock transaction data pool with different users
    all_mock_transactions = [
        # User 1 transactions
        TransactionResponse(
            id=uuid4(),
            user_id="user_123",
            currency="coins",
            type="spend",
            amount=20,
            source="coach_hiring",
            timestamp=datetime.now() - timedelta(hours=2)
        ),
        TransactionResponse(
            id=uuid4(),
            user_id="user_123",
            currency="gems",
            type="earn",
            amount=5,
            source="match_win",
            timestamp=datetime.now() - timedelta(hours=5)
        ),
        TransactionResponse(
            id=uuid4(),
            user_id="user_123",
            currency="coins",
            type="earn",
            amount=150,
            source="match_win",
            timestamp=datetime.now() - timedelta(days=1)
        ),
        # User 2 transactions
        TransactionResponse(
            id=uuid4(),
            user_id="user_456",
            currency="gems",
            type="spend",
            amount=10,
            source="pack_purchase",
            timestamp=datetime.now() - timedelta(days=1, hours=3)
        ),
        TransactionResponse(
            id=uuid4(),
            user_id="user_456",
            currency="coins",
            type="earn",
            amount=75,
            source="daily_bonus",
            timestamp=datetime.now() - timedelta(days=2)
        ),
        # User 3 transactions
        TransactionResponse(
            id=uuid4(),
            user_id="user_789",
            currency="gems",
            type="earn",
            amount=3,
            source="achievement",
            timestamp=datetime.now() - timedelta(days=2, hours=8)
        ),
        TransactionResponse(
            id=uuid4(),
            user_id="user_789",
            currency="coins",
            type="spend",
            amount=50,
            source="coach_hiring",
            timestamp=datetime.now() - timedelta(days=3)
        ),
        # More user_123 transactions
        TransactionResponse(
            id=uuid4(),
            user_id="user_123",
            currency="coins",
            type="earn",
            amount=200,
            source="match_win",
            timestamp=datetime.now() - timedelta(days=3, hours=6)
        ),
        TransactionResponse(
            id=uuid4(),
            user_id="user_123",
            currency="gems",
            type="spend",
            amount=15,
            source="pack_purchase",
            timestamp=datetime.now() - timedelta(days=4)
        ),
        TransactionResponse(
            id=uuid4(),
            user_id="user_123",
            currency="coins",
            type="earn",
            amount=100,
            source="weekly_bonus",
            timestamp=datetime.now() - timedelta(days=5)
        ),
        TransactionResponse(
            id=uuid4(),
            user_id="user_123",
            currency="gems",
            type="earn",
            amount=8,
            source="match_win",
            timestamp=datetime.now() - timedelta(days=5, hours=4)
        ),
        TransactionResponse(
            id=uuid4(),
            user_id="user_123",
            currency="coins",
            type="spend",
            amount=30,
            source="coach_hiring",
            timestamp=datetime.now() - timedelta(days=6)
        )
    ]
    
    # Filter transactions by user_id
    user_transactions = [tx for tx in all_mock_transactions if tx.user_id == user_id]
    
    # Sort by timestamp (most recent first)
    user_transactions.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Apply limit
    if limit:
        return user_transactions[:limit]
    
    return user_transactions
