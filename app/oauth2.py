from jose import JWTError, jwt
from datetime import datetime, timedelta
import app.schemas as schemas
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
EXPIRES = settings.expires


def create_jwt(data: dict):
    enc = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRES)
    enc.update({'exp': expire})
    
    encoded = jwt.encode(enc, SECRET_KEY, algorithm=ALGORITHM)
    return encoded

def verify_token(token: str, exception):
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=ALGORITHM)
        account_number: int = payload.get("account_number")
        # print(payload)
        
        if account_number is None:
            raise exception
        token_data = schemas.TokenData(account_number=account_number).account_number
    except JWTError: 
        raise exception
    return token_data
    

def get_current_user(token: str = Depends(oauth2_scheme)):
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to access this", headers={"WWW-Authenticate": "Bearer"})
    # print(verify_token(token, exception))
    
    return verify_token(token, exception)