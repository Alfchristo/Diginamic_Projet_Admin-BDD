import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

# Connexion à la base de données MongoDB
client = MongoClient('mongodb://localhost:27017/')
database = client['projetseo']

# Sélection de la collection
collection = database['urls']
pending_urls_collection = database['pending_urls']

new_document = {'url': 'https://quotes.toscrape.com/page/2/', 'scope': 'https://quotes.toscrape.com',
                'status': 'pending'}
result_url = pending_urls_collection.insert_one(new_document)


# Document à insérer
nouveau_document = {
    'url': 'https://quotes.toscrape.com/page/2/',
    'scope': 'https://quotes.toscrape.com',
    'status': 'pending'
}

# Insertion du document dans la collection
result = collection.insert_one(nouveau_document)

# Vérification du succès de l'insertion
if result.inserted_id:
    print(f"Document inséré avec succès. ID: {result.inserted_id}")
else:
    print("Échec de l'insertion du document.")