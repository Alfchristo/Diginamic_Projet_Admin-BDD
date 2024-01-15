import time
from pymongo import MongoClient

# Se connecter à la base de données MongoDB
client = MongoClient('mongodb://localhost:27017/')
database = client['projetseo']
logs_collection = database['logs']


def log_event(message):
    # Insertion d'un journal d'événement dans la collection 'logs'
    logs_collection.insert_one({"type": "event", "timestamp": time.time(), "message": message})


def log_error(url, error_message):
    # Insérer un journal d'erreur dans la collection 'logs'
    logs_collection.insert_one({"type": "error", "timestamp": time.time(), "url": url, "message": error_message})
