from fastapi import FastAPI
from .api.wallet import router as wallet_router
from .api.salary import router as salary_router


from backend.app.db.database import engine
from backend.app.models import Base, User, Wallet
from sqlalchemy.orm import Session

app = FastAPI()
app.include_router(wallet_router)
app.include_router(salary_router)

# Ensure test user and wallet exist at startup
@app.on_event("startup")
def seed_test_user_wallet():
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as db:
        user = db.query(User).filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser", email="testuser@example.com")
            db.add(user)
            db.commit()
            db.refresh(user)
        wallet = db.query(Wallet).filter_by(user_id=user.id).first()
        if not wallet:
            wallet = Wallet(user_id=user.id, coins=100, gems=10, credits=50)
            db.add(wallet)
            db.commit()
