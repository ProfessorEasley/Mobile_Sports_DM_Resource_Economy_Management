from .db.database import SessionLocal
from .models import User


def get_current_user():
    """
    Simple auth stub: return the seeded test user as an object with a numeric ID. 
    Ensures wallet queries can locate the correct record.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser", email="testuser@example.com")
            db.add(user)
            db.commit()
            db.refresh(user)
        return {"user_id": user.id}
    finally:
        db.close()
