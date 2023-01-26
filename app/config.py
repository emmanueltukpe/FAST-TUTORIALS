from pydantic import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    database: str
    account_collection: str
    transaction_collection: str
    secret_key: str
    algorithm: str
    expires: int
    url: str
    
    class Config:
        env_file = ".env"
    
settings = Settings() 