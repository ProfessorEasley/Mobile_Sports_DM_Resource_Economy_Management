from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    wallets = relationship("Wallet", back_populates="user")

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coins = Column(BigInteger, default=0)
    gems = Column(BigInteger, default=0)
    credits = Column(BigInteger, default=0)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="wallets")
    logs = relationship("AuditLog", back_populates="wallet")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    currency_type = Column(String(16), nullable=False)
    operation = Column(String(16), nullable=False)
    amount = Column(BigInteger, nullable=False)
    balance_after = Column(BigInteger, nullable=False)
    meta = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    wallet = relationship("Wallet", back_populates="logs")
