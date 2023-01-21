from fastapi import HTTPException, Depends, status
from passlib.context import CryptContext
from random import randint
from app.db import get_db
from sqlalchemy.orm import Session
import app.models as models
import requests
from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def generate_unique_number():
    return randint(100000000, 999999999)


def verify(given_password: str, hashed_password: str):
    return pwd_context.verify(given_password, hashed_password)


def convert_btc_to_naira(btc_amount: float):
    url = settings.url
    response = requests.get(url)
    data = response.json()
    rate = data["bpi"]["NGN"]["rate_float"]
    naira_amount = rate * btc_amount
    return naira_amount


def convert_naira_to_btc(naira_amount: float):
    url = settings.url
    response = requests.get(url)
    data = response.json()
    rate = data["bpi"]["NGN"]["rate_float"]
    btc_amount = naira_amount / rate
    return btc_amount


def get_account(account_number: int, db: Session):
    account = db.query(models.Account).filter(
        models.Account.account_number == account_number)
    print(account)
    if account.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return account


def debit(account_number: int, amount: float, db: Session):
    account = get_account(account_number, db)
    account_balance = account.first().naira_balance
    if account_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient Funds")
    new_bal = account_balance - amount
    account.update({models.Account.naira_balance: new_bal},
                   synchronize_session=False)
    db.commit()
    return account.first()


def credit(account_number: int, amount: float, db: Session):
    account = get_account(account_number, db)
    account_balance = account.first().naira_balance
    new_bal = account_balance + amount
    account.update({models.Account.naira_balance: new_bal},
                   synchronize_session=False)
    db.commit()
    return account.first()


def convert_btc_N(account_number: int, amount: float, db: Session):
    account = get_account(account_number, db)
    btc_balance = account.first().bitcoin_balance
    if btc_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have sufficient coins for this operation")
    new_bal_btc = btc_balance - amount
    converted = convert_btc_to_naira(amount)
    new_bal = account.first().naira_balance + converted
    account.update({models.Account.naira_balance: new_bal,
                   models.Account.bitcoin_balance: new_bal_btc}, synchronize_session=False)
    db.commit()
    return account.first()


def convert_N_btc(account_number: int, amount: float, db: Session):
    account = get_account(account_number, db)
    naira_balance = account.first().naira_balance
    if naira_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have sufficient money for this operation")
    new_bal_naira = naira_balance - amount
    converted = convert_naira_to_btc(amount)
    new_bal = account.first().bitcoin_balance + converted
    account.update({models.Account.bitcoin_balance: new_bal,
                   models.Account.naira_balance: new_bal_naira}, synchronize_session=False)
    db.commit()
    return account.first()

def transfer(account_number: int, sender_account: int, amount: float, db: Session):
    account = get_account(account_number, db)
    btc_balance = account.first().bitcoin_balance
    if btc_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You do not have sufficient coins for this operation")
    sender = get_account(sender_account, db)
    res_new_balance = btc_balance - amount
    sender_bal = sender.first().bitcoin_balance
    new_sender_bal  = sender_bal + amount
    account.update({models.Account.bitcoin_balance: res_new_balance}, synchronize_session=False)
    db.commit()
    sender.update({models.Account.bitcoin_balance: new_sender_bal}, synchronize_session=False)
    db.commit()
    return account.first()
    