from pymongo import MongoClient, ASCENDING

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
database = client['projetseo']
urls_collection = database['urls']
pages_metadata_collection = database['pages_metadata']
logs_collection = database['logs']

# Ajout des index
urls_collection.create_index([("url", ASCENDING)], unique=True)
urls_collection.create_index([("status", ASCENDING)])
pages_metadata_collection.create_index([("url", ASCENDING)], unique=True)

# Commentaires
"""
Ce script se connecte à une instance MongoDB locale sur le port 27017.
Il initialise les collections pour stocker des URLs, des métadonnées de pages et des journaux.
Des index sont ensuite créés pour optimiser les requêtes sur les collections.
"""

# Explications
"""
1. Connexion à MongoDB :
   - `client` : Connexion au serveur MongoDB local.
   - `database` : Base de données utilisée dans MongoDB, nommée 'projetseo'.
   - Collections MongoDB :
     - `urls_collection` : Collection pour stocker les URLs.
     - `pages_metadata_collection` : Collection pour stocker les métadonnées des pages.
     - `logs_collection` : Collection pour stocker les logs.

2. Ajout des index :
   - Pour `urls_collection` :
     - Index unique sur le champ "url" pour assurer l'unicité des URLs.
     - Index sur le champ "status" pour optimiser les requêtes basées sur le statut.
   - Pour `pages_metadata_collection` :
     - Index unique sur le champ "url" pour assurer l'unicité des URLs dans les métadonnées de pages.
"""

