from fastapi import HTTPException, status
from passlib.context import CryptContext
from random import randint
from app.db import account_collection
import requests
from app.config import settings
from uuid import uuid4


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


def get_account(account_number: int):
    account  = account_collection.find_one({"account_number": account_number})
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return account


class TransactionsMethods:
    
    def debit(account_number: int, amount: float):
        account = get_account(account_number)
        account_balance = account["naira_balance"]
        if account_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient Funds")
        new_bal = account_balance - amount
        update =account_collection.find_one_and_update({"account_number": account_number},
                    {"$set": {"naira_balance": new_bal}})
        return update

    def credit(account_number: int, amount: float):
        account = get_account(account_number)
        account_balance = account["naira_balance"]
        new_bal = account_balance + amount
        print(new_bal)
        update =account_collection.find_one_and_update({"account_number": account_number},
                    {"$set": {"naira_balance": new_bal}})
        print(update)
        return update


    def convert_btc_N(account_number: int, amount: float):
        account = get_account(account_number)
        btc_balance = account["bitcoin_balance"]
        if btc_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You do not have sufficient coins for this operation")
        new_bal_btc = btc_balance - amount
        converted = convert_btc_to_naira(amount)
        new_bal = account["naira_balance"] + converted
        update =account_collection.find_one_and_update({"account_number": account_number},
                    {"$set": {"naira_balance": new_bal, "bitcoin_balance": new_bal_btc}})
        return update


    def convert_N_btc(account_number: int, amount: float):
        account = get_account(account_number)
        naira_balance = account["naira_balance"]
        if naira_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You do not have sufficient money for this operation")
        new_bal_naira = naira_balance - amount
        converted = convert_naira_to_btc(amount)
        new_bal = account["bitcoin_balance"] + converted
        update =account_collection.find_one_and_update({"account_number": account_number},
                    {"$set": {"naira_balance": new_bal_naira, "bitcoin_balance": new_bal}})
        return update


    def transfer(account_number: int, recipient_account: int, amount: float):
        account = get_account(account_number)
        btc_balance = account["bitcoin_balance"]
        if btc_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You do not have sufficient coins for this operation")
        recipient = get_account(recipient_account)
        res_new_balance = btc_balance - amount
        recipient_bal = recipient["bitcoin_balance"]
        new_recipient_bal  = recipient_bal + amount
        account_collection.find_one_and_update({"account_number": account_number},
                    {"$set": {"bitcoin_balance": res_new_balance}})
        account_collection.find_one_and_update({"account_number": recipient_account},
                    {"$set": {"bitcoin_balance": new_recipient_bal}})
        return "success"


def get_uuid() -> str:
    """Returns an unique UUID (UUID4)"""
    return str(uuid4())