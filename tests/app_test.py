import pytest
from fastapi.testclient import TestClient
from jose import jwt
from app.main import app
from app import schemas
from app.db import account_collection
from app.config import settings
from app.utils import convert_btc_to_naira, convert_naira_to_btc

client = TestClient(app)


def test_create_account():
    res = client.post("/accounts/", json={
        "account_name": "Chidalu",
        "password": "otugbokindi"
    })
    created = schemas.AccountResponse(**res.json())
    assert res.status_code == 201
    assert created.account_name == "Chidalu"


def test_login(test_account):
    res = client.post("/accounts/login", data={
                      "username": test_account["account_number"], "password": test_account["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=settings.algorithm)
    account_number: int = payload.get("account_number")
    assert account_number == test_account["account_number"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("username, password, status_code", [
    (None, None, 422),
    ("457826396", "agenda", 403),
    ("818295806", None, 422),
    (None, "youknow", 422)
])
def test_incorrect_login(username, password, status_code):
    res = client.post("/accounts/login",
                      data={"username": username, "password": password})
    assert res.status_code == status_code


def test_get_account(test_account):
    account_number = test_account["account_number"]
    res = client.get(f"/accounts/{account_number}")
    created = schemas.AccountResponse(**res.json())
    assert res.status_code == 200
    assert created.account_name == test_account["account_name"]


@pytest.mark.parametrize("account_number, status_code", [
    ("faithokolie", 422),
    ("4578266", 404),
])
def test_get_account_error(account_number, status_code):
    res = client.get(f"/accounts/{account_number}")
    assert res.status_code == status_code


def test_fund(verified_client):
    amount = 8000
    res = verified_client.post("/transactions/fund", json={
        "amount": amount,
    })
    transaction = schemas.FundResponse(**res.json())
    get_account = account_collection.find_one(
        {"account_number": transaction.recipient_account_number})
    assert res.status_code == 201
    assert get_account["naira_balance"] == 8000


def test_fund_unauthorized(client):
    amount = 8000
    res = client.post("/transactions/fund", json={
        "amount": amount,
    })
    assert res.status_code == 401


@pytest.mark.parametrize("amount, status_code, links", [
    (None, 422, "/transactions/fund"),
    ("Jamiu", 422, "/transactions/fund"),
    (None, 422, "/transactions/withdraw"),
    ("Jamiu", 422, "/transactions/withdraw"),
    (None, 422, "/transactions/convert/n-btc"),
    ("Jamiu", 422, "/transactions/convert/n-btc"),
    (None, 422, "/transactions/convert/btc-n"),
    ("Jamiu", 422, "/transactions/convert/btc-n")
])
def test_type_error(verified_client, amount, status_code, links):
    res = verified_client.post(f"{links}", json={
        "amount": amount,
    })
    assert res.status_code == status_code


def test_withdrawal(verified_client):
    credit = 120000
    debit = 10000
    verified_client.post("/transactions/fund", json={
        "amount": credit,
    })
    withdraw = verified_client.post("/transactions/withdraw", json={
        "amount": debit,
    })
    transaction = schemas.WithdrawalResponse(**withdraw.json())
    get_account = account_collection.find_one(
        {"account_number": transaction.sender_account_number})
    assert withdraw.status_code == 201
    assert get_account["naira_balance"] == 110000


def test_withdrawal_unauthorized(client):
    debit = 10000
    withdraw = client.post("/transactions/withdraw", json={
        "amount": debit,
    })
    assert withdraw.status_code == 401


def test_withdrawal_insufficient_funds(verified_client):
    debit = 10000
    withdraw = verified_client.post("/transactions/withdraw", json={
        "amount": debit,
    })
    assert withdraw.status_code == 403


def test_convert_naira_to_btc(verified_client):
    credit = 12000000
    convert = 1000000
    fund_transaction = verified_client.post("/transactions/fund", json={
        "amount": credit,
    })
    transaction_init = schemas.FundResponse(**fund_transaction.json())
    get_account_init = account_collection.find_one(
        {"account_number": transaction_init.recipient_account_number})
    converted_transaction = verified_client.post("/transactions/convert/n-btc", json={
        "amount": convert,
    })
    transaction = schemas.FundResponse(**converted_transaction.json())
    get_account = account_collection.find_one(
        {"account_number": transaction.recipient_account_number})
    assert converted_transaction.status_code == 201
    assert get_account["naira_balance"] == 11000000
    assert get_account["bitcoin_balance"] == get_account_init["bitcoin_balance"] + \
        convert_naira_to_btc(convert)


def test_convert_naira_to_btc_unauthorized(client):
    convert = 10000
    transaction = client.post("/transactions/convert/n-btc", json={
        "amount": convert,
    })
    assert transaction.status_code == 401


def test_convert_naira_to_btc_insufficient_funds(verified_client):
    convert = 10000
    transaction = verified_client.post("/transactions/convert/n-btc", json={
        "amount": convert,
    })
    assert transaction.status_code == 403


def test_convert_btc_to_naira(verified_client):
    credit = 21
    convert = 2.43
    fund_transaction = verified_client.post("/transactions/fund", json={
        "amount": credit,
    })
    transaction_init = schemas.FundResponse(**fund_transaction.json())
    get_account_init = account_collection.find_one_and_update(
        {"account_number": transaction_init.recipient_account_number}, {"$set": {"bitcoin_balance": credit}})
    converted_transaction = verified_client.post("/transactions/convert/btc-n", json={
        "amount": convert,
    })
    transaction = schemas.FundResponse(**converted_transaction.json())
    get_account = account_collection.find_one(
        {"account_number": transaction.recipient_account_number})
    assert converted_transaction.status_code == 201
    assert get_account["bitcoin_balance"] == 18.57
    assert get_account["naira_balance"] == get_account_init["naira_balance"] + \
        convert_btc_to_naira(convert)


def test_convert_btc_to_naira_unauthorized(client):
    convert = 100
    transaction = client.post("/transactions/convert/btc-n", json={
        "amount": convert,
    })
    assert transaction.status_code == 401


def test_convert_btc_to_naira_insufficient_funds(verified_client):
    convert = 10
    transaction = verified_client.post("/transactions/convert/btc-n", json={
        "amount": convert,
    })
    assert transaction.status_code == 403

def test_transfers(verified_client, test_alt_account):
    credit = 21
    amount = 10
    fund_transaction = verified_client.post("/transactions/fund", json={
        "amount": credit,
    })
    transaction_init = schemas.FundResponse(**fund_transaction.json())
    account_collection.find_one_and_update(
        {"account_number": transaction_init.recipient_account_number}, {"$set": {"bitcoin_balance": credit}})
    get_account_init = account_collection.find_one(
        {"account_number": transaction_init.recipient_account_number})
    transfer = verified_client.post("/transactions/transfers", json={
        "amount": amount,
        "recipient_account_number": test_alt_account["account_number"]
    })
    transfer_res = schemas.TransferResponse(**transfer.json())
    get_account = account_collection.find_one(
        {"account_number": transfer_res.sender_account_number})
    get_recipient_account = account_collection.find_one(
        {"account_number": test_alt_account["account_number"]})
    
    assert get_account["bitcoin_balance"] == get_account_init["bitcoin_balance"] - amount
    assert get_recipient_account["bitcoin_balance"] == amount
    assert transfer.status_code == 201
    
def test_transfers_unauthenticated(client, test_alt_account):
    amount = 10
    transfer = client.post("/transactions/transfers", json={
        "amount": amount,
        "recipient_account_number": test_alt_account["account_number"]
    })
    assert transfer.status_code == 401
    
def test_transfers_insufficient_funds(verified_client, test_alt_account):
    amount = 10
    transfer = verified_client.post("/transactions/transfers", json={
        "amount": amount,
        "recipient_account_number": test_alt_account["account_number"]
    })
    assert transfer.status_code == 403
    

@pytest.mark.parametrize("amount, recipient_account_number, status_code", [
    (None, None, 422),
    (4, None, 422),
    (None, 818295806, 422)
])
def test_transfers_pydantic_error(verified_client, amount, recipient_account_number, status_code):
    transfer = verified_client.post("/transactions/transfers", json={
        "amount": amount,
        "recipient_account_number": recipient_account_number
    })
    assert transfer.status_code == status_code
    
def test_root(clear_db):
    res = client.get("/")
    assert res.json() == {"Hello": "World!!!"}
    assert res.status_code == 200
