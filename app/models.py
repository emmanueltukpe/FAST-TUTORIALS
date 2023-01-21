from app.db import Base
from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from enum import Enum
# from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    is_loved = Column(Boolean, server_default="FALSE")
    time = Column(TIMESTAMP(timezone=True), nullable=False,
                  server_default=text('now()'))

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, nullable=False)
    account_number = Column(Integer, nullable=False, unique=True)
    account_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    naira_balance = Column(Float, nullable=False, server_default="0")
    bitcoin_balance = Column(Float, nullable=False, server_default="0")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, nullable=False)
    sender_account_number = Column(String, nullable=True)
    recipient_account_number = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    # account_id = Column(Intteger, Foreign_key("accounts.id", ondelete="CASCADE"), nullable=False)
    # account = relationship("Account")