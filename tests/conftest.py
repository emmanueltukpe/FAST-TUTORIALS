import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.oauth2 import create_jwt
from app.db import account_collection, transaction_collection


client = TestClient(app)


@pytest.fixture()
def client():
    yield TestClient(app)


@pytest.fixture()
def test_account(client):
    data = {
        "account_name": "Chidalu",
        "password": "otugbokindi"
    }
    res = client.post("/accounts/", json=data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = data['password']
    return new_user

@pytest.fixture()
def test_alt_account(client):
    data = {
        "account_name": "Chidalu",
        "password": "otugbokindi"
    }
    res = client.post("/accounts/", json=data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = data['password']
    return new_user



@pytest.fixture
def token(test_account):
    return create_jwt({"account_number": test_account["account_number"]})


@pytest.fixture
def verified_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def clear_db(test_account, test_alt_account):
    account_collection.delete_many(
        {"account_name": test_account["account_name"]})
    account_collection.delete_many(
        {"account_name": test_alt_account["account_name"]})
    transaction_collection.delete_many({"sender_account_number": test_account["account_number"]})
    transaction_collection.delete_many({"recipient_account_number": test_account["account_number"]})
    transaction_collection.delete_many({"recipient_account_number": test_alt_account["account_number"]})
    
    return "done"
