from fastapi import FastAPI
import app.models as models
from app.db import engine
from app.routers import users, accounts, tansactions
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware

print(settings.database_hostname)
    
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# try:
#     conn = psycopg2.connect(host='localhost', database='fast api', user='postgres',
#                             password='emma', cursor_factory=RealDictCursor, port=4100)
#     cursor = conn.cursor()
#     print("Database connection established")
# except Exception as err:
#     print("Error: ", err)



app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(tansactions.router)

@app.get("/")
def read_root():
    return {"Hello": "World!!!"}



