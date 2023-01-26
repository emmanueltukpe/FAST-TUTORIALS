from fastapi import FastAPI
import app.models as models
# from app.db import engine
from app.routers import accounts, tansactions
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(accounts.router)
app.include_router(tansactions.router)

@app.get("/")
def read_root():
    return {"Hello": "World!!!"}



