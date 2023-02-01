import pytest
from fastapi.testclient import TestClient
from jose import jwt
from app.main import app
from app import schemas
from app.db import account_collection, transaction_collection
from app.config import settings

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
    res =  client.post("/accounts/login", data={"username": test_account["account_number"], "password": test_account["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key,algorithms=settings.algorithm)
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
    res =  client.post("/accounts/login", data={"username": username, "password": password})
    assert res.status_code == status_code

def test_get_account(test_account):
    account_number = test_account["account_number"]
    res =  client.get(f"/accounts/{account_number}")
    created = schemas.AccountResponse(**res.json())
    assert res.status_code == 200
    assert created.account_name ==  test_account["account_name"]


@pytest.mark.parametrize("account_number, status_code", [
    ("faithokolie", 422),
    ("4578266", 404),
])
def test_get_account_error(account_number, status_code):
    res =  client.get(f"/accounts/{account_number}")
    assert res.status_code == status_code
    
def test_fund(verified_client, test_account_with_money):
    amount = 8000
    res = verified_client.post("/transactions/fund", json={
    "amount": amount,
    })
    assert res.status_code == 201
    assert test_account_with_money["naira_balance"] == 8000
    
def test_root(clear_db):
    res = client.get("/")
    assert res.json() == {"Hello": "World!!!"}
    assert res.status_code == 200