from pymongo import MongoClient

# Connexion à la base de données MongoDB
client = MongoClient('mongodb://localhost:27017/')
database = client['projetseo']

# Sélection de la collection
collection = database['urls']
url_en_attente = database['urls_en_attente']
# Create or get the 'pages' collection
pages_metadata = database['pages_metadata']

new_document = {'url': 'https://quotes.toscrape.com/page/2/', 'scope': 'https://quotes.toscrape.com',
                'status': 'pending'}
result_url = url_en_attente.insert_one(new_document)


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