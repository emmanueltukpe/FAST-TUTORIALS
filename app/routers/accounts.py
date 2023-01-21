from fastapi import HTTPException, status, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import app.models as models
from app.db import get_db
from app.schemas import AccountCreate, AccountResponse, AccountLogin
import app.utils
import app.oauth2


router = APIRouter(prefix="/accounts", tags=['Accounts'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    hashed_password = app.utils.hash(account.password)
    account.password = hashed_password
    accounts = models.Account(
        **account.dict(), account_number=app.utils.generate_unique_number())
    db.add(accounts)
    db.commit()
    db.refresh(accounts)
    return accounts


@router.get("/{id}", response_model=AccountResponse)
def get_account(id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == id).first()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return account


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(
        models.Account.account_number == request.username).first()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account number or password")
    if not app.utils.verify(request.password, account.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account number or password")
    access_token =  app.oauth2.create_jwt(data= {"account_number": account.account_number })
    return {"access_token": access_token, "token_type": "bearer"}