from pymongo import MongoClient
from app.config import settings
from pymongo.collection import Collection


client = MongoClient(settings.mongo_uri)


account_collection: Collection = client[settings.database][settings.account_collection]
transaction_collection: Collection = client[settings.database][settings.transaction_collection]