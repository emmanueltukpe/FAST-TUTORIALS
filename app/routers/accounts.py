from fastapi import HTTPException, status, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
import app.models as models
# from app.db import get_db
from app.schemas import AccountCreate, AccountResponse
import app.utils
from app.db import account_collection
import app.oauth2


router = APIRouter(prefix="/accounts", tags=['Accounts'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
def create_account(account: AccountCreate):
    return models.AccountsRepo.create_account(account)


@router.get("/{account_number}", response_model=AccountResponse)
def get_account(account_number: int):
    account  = account_collection.find_one({"account_number": account_number})
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return account


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends()):
    account  = account_collection.find_one({"account_number": int(request.username)})
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account number or password")
    if not app.utils.verify(request.password, account["password"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account number or password")
    access_token =  app.oauth2.create_jwt(data= {"account_number": account["account_number"] })
    return {"access_token": access_token, "token_type": "bearer"}