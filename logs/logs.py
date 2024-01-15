import time
from pymongo import MongoClient

# Connect to the MongoDB database (adjust the connection string as needed)
client = MongoClient('mongodb://localhost:27017/')
database = client['projetseo']
logs_collection = database['logs']


def log_event(message):
    # Insert an event log into the 'logs' collection
    logs_collection.insert_one({"type": "event", "timestamp": time.time(), "message": message})


def log_error(url, error_message):
    # Insert an error log into the 'logs' collection
    logs_collection.insert_one({"type": "error", "timestamp": time.time(), "url": url, "message": error_message})
