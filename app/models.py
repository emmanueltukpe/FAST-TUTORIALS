from app.schemas import AccountCreate, Transaction, Transfer
from app.utils import get_uuid, generate_unique_number, hash, TransactionsMethods
from app.db import account_collection, transaction_collection


class AccountsRepo:
    @staticmethod
    def create_account(account: AccountCreate):
        hashed = hash(account.password)
        account.password = hashed
        document = account.dict()
        document["account_number"] = generate_unique_number()
        document["naira_balance"] = 0.0
        document["bitcoin_balance"] = 0.0
        document["_id"] = get_uuid()
        res = account_collection.insert_one(document)
        assert res.acknowledged

        return account_collection.find_one({"_id": res.inserted_id})


class TransactionsRepo:
    @staticmethod
    def credit(transaction: Transaction, account_number: int):
        amount = transaction.amount
        TransactionsMethods.credit(account_number, amount)
        document = transaction.dict()
        document["recipient_account_number"] = account_number
        document["transaction_type"] = "Credit"
        document["_id"] = get_uuid()
        res = transaction_collection.insert_one(document)
        assert res.acknowledged

        return transaction_collection.find_one({"_id": res.inserted_id})

    @staticmethod
    def debit(transaction: Transaction, account_number: int):
        amount = transaction.amount
        TransactionsMethods.debit(account_number, amount)
        document = transaction.dict()
        document["sender_account_number"] = account_number
        document["transaction_type"] = "Debit"
        document["_id"] = get_uuid()
        res = transaction_collection.insert_one(document)
        assert res.acknowledged

        return transaction_collection.find_one({"_id": res.inserted_id})

    @staticmethod
    def naria_bitcoin_converter(transaction: Transaction, account_number: int):
        amount = transaction.amount
        TransactionsMethods.convert_N_btc(account_number, amount)
        document = transaction.dict()
        document["recipient_account_number"] = account_number
        document["transaction_type"] = "Conversion"
        document["_id"] = get_uuid()
        res = transaction_collection.insert_one(document)
        assert res.acknowledged

        return transaction_collection.find_one({"_id": res.inserted_id})

    @staticmethod
    def bitcoin_naira_converter(transaction: Transaction, account_number: int):
        amount = transaction.amount
        TransactionsMethods.convert_btc_N(account_number, amount)
        document = transaction.dict()
        document["recipient_account_number"] = account_number
        document["transaction_type"] = "Conversion"
        document["_id"] = get_uuid()
        res = transaction_collection.insert_one(document)
        assert res.acknowledged

        return transaction_collection.find_one({"_id": res.inserted_id})

    @staticmethod
    def transfer(transfer: Transfer, account_number: int):
        amount = transfer.amount
        TransactionsMethods.transfer(
            account_number, transfer.recipient_account_number, amount)
        document = transfer.dict()
        document["sender_account_number"] = account_number
        document["transaction_type"] = "Transfer"
        document["_id"] = get_uuid()
        res = transaction_collection.insert_one(document)
        assert res.acknowledged

        return transaction_collection.find_one({"_id": res.inserted_id})
