from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
import app.models as models
from app.db import get_db
import app.utils as utils
import app.oauth2 as oauth2
from app.schemas import Transaction, Transfer

router = APIRouter(prefix="/transactions", tags=['Transactions'])


@router.post("/fund", status_code=status.HTTP_201_CREATED)
def fund(transaction: Transaction, db: Session = Depends(get_db), account_number: int = Depends(oauth2.get_current_user)):
    amount = transaction.amount
    utils.credit(account_number, amount, db)
    transactions = models.Transaction(
        **transaction.dict(), recipient_account_number=account_number, transaction_type="fund")
    db.add(transactions)
    db.commit()
    db.refresh(transactions)
    return transactions


@router.post("/withdraw", status_code=status.HTTP_201_CREATED)
def withdraw(transaction: Transaction, db: Session = Depends(get_db), account_number: int = Depends(oauth2.get_current_user)):
    amount = transaction.amount
    utils.debit(account_number, amount, db)
    transactions = models.Transaction(
        **transaction.dict(), recipient_account_number=account_number, transaction_type="withdrawal")
    db.add(transactions)
    db.commit()
    db.refresh(transactions)
    return transactions


@router.post("/convert/btc-n", status_code=status.HTTP_201_CREATED)
def convert_btc_to_N(transaction: Transaction, db: Session = Depends(get_db), account_number: int = Depends(oauth2.get_current_user)):
    amount = transaction.amount
    utils.convert_btc_N(account_number, amount, db)
    transactions = models.Transaction(
        **transaction.dict(), recipient_account_number=account_number, transaction_type="Conversion")
    db.add(transactions)
    db.commit()
    db.refresh(transactions)
    return transactions


@router.post("/convert/n-btc", status_code=status.HTTP_201_CREATED)
def convert_N_to_btc(transaction: Transaction, db: Session = Depends(get_db), account_number: int = Depends(oauth2.get_current_user)):
    amount = transaction.amount
    utils.convert_N_btc(account_number, amount, db)
    transactions = models.Transaction(
        **transaction.dict(), recipient_account_number=account_number, transaction_type="Conversion")
    db.add(transactions)
    db.commit()
    db.refresh(transactions)
    return transactions

@router.post("/transfers", status_code=status.HTTP_201_CREATED)
def transfers(transfers: Transfer, db: Session = Depends(get_db), account_number: int = Depends(oauth2.get_current_user)):
    amount = transfers.amount
    sender = transfers.sender_account_number
    utils.transfer(account_number, sender, amount, db)
    transactions = models.Transaction(
        **transfers.dict(), recipient_account_number=account_number, transaction_type="Transfer")
    db.add(transactions)
    db.commit()
    db.refresh(transactions)
    return transactions