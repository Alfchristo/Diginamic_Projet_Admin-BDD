from datetime import datetime
from pymongo import MongoClient

# Connexion à MongoDB pour les journaux
client = MongoClient('mongodb://localhost:27017/')
logs_collection = client['test']['logs']

def log_error(url, message):
    """
    Enregistre un message d'erreur dans la collection de logs.

    Args:
    - url (str): URL associée à l'erreur.
    - message (str): Message d'erreur à enregistrer.

    Returns:
    - None
    """
    log = {
        "url": url,
        "message": message,
        "type": "error",
        "timestamp": datetime.now()
    }
    logs_collection.insert_one(log)
    print(f"ERROR: {message} for URL: {url}")

def log_event(message):
    """
    Enregistre un événement dans la collection de logs.

    Args:
    - message (str): Message de l'événement à enregistrer.

    Returns:
    - None
    """
    log = {
        "message": message,
        "type": "event",
        "timestamp": datetime.now()
    }
    logs_collection.insert_one(log)
    print(f"EVENT: {message}")
