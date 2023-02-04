from fastapi import status, Depends, APIRouter
import app.models as models
import app.oauth2 as oauth2
from app.schemas import Transaction, Transfer, TransferResponse, FundResponse, WithdrawalResponse

router = APIRouter(prefix="/transactions", tags=['Transactions'])


@router.post("/fund", status_code=status.HTTP_201_CREATED, response_model=FundResponse)
def fund(transaction: Transaction, account_number: int = Depends(oauth2.get_current_user)):
    return models.TransactionsRepo.credit(transaction, account_number)


@router.post("/withdraw", status_code=status.HTTP_201_CREATED, response_model=WithdrawalResponse)
def withdraw(transaction: Transaction, account_number: int = Depends(oauth2.get_current_user)):
    return models.TransactionsRepo.debit(transaction, account_number)


@router.post("/convert/btc-n", status_code=status.HTTP_201_CREATED, response_model=FundResponse)
def convert_btc_to_N(transaction: Transaction, account_number: int = Depends(oauth2.get_current_user)):
    return models.TransactionsRepo.bitcoin_naira_converter(transaction, account_number)


@router.post("/convert/n-btc", status_code=status.HTTP_201_CREATED, response_model=FundResponse)
def convert_N_to_btc(transaction: Transaction, account_number: int = Depends(oauth2.get_current_user)):
    return models.TransactionsRepo.naria_bitcoin_converter(transaction, account_number)


@router.post("/transfers", status_code=status.HTTP_201_CREATED, response_model=TransferResponse)
def transfers(transfers: Transfer, account_number: int = Depends(oauth2.get_current_user)):
    return models.TransactionsRepo.transfer(transfers, account_number)
