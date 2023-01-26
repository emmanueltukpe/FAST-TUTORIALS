from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: str
    is_loved: bool = True
    
class User(UserBase):
    pass 
        
        
class ResponseUser(UserBase):
    id: int
    time: datetime
    class Config:
        orm_mode = True 
        
class AccountCreate(BaseModel):
    account_name: str
    password: str

class AccountResponse(BaseModel):
    account_name: str
    account_number: int
    bitcoin_balance: float
    naira_balance: float 
    _id: str
    class Config:
        orm_mode = True 
        
class AccountLogin(BaseModel):
    account_number: int
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    account_number: Optional[int]

class Transaction(BaseModel):
    amount: float
    
class Transfer(Transaction):
    recipient_account_number: int
