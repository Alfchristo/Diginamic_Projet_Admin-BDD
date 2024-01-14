import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests

# Connexion à la base de données MongoDB
client = MongoClient('mongodb://localhost:27017/')
database = client['projetseo']  # Remplacez 'votre_base_de_donnees' par le nom de votre base de données

# Sélection de la collection
collection = database['urls']

# Document à insérer
nouveau_document = {
    'url': 'https://quotes.toscrape.com/page/2/',
    'scope': 'https://quotes.toscrape.com/',
    'status': 'pending'
}

# Insertion du document dans la collection
result = collection.insert_one(nouveau_document)

# Vérification du succès de l'insertion
if result.inserted_id:
    print(f"Document inséré avec succès. ID: {result.inserted_id}")
else:
    print("Échec de l'insertion du document.")

def get_pending_url(db):
    url_document = db.find_one_and_update({"status": "pending"},
                                          {"$set": {"status": "processing"}},
                                          return_document=pymongo.ReturnDocument.BEFORE
                                          )

    if url_document:
        return url_document["url"]
    else:
        return None


def set_url_completed(db, url):
    # Marque l'URL comme traitée dans la base de données
    db.update_one({"url": url}, {"$set": {"status": "completed"}})


def simple_scrape(db, url):

    if url:
        # Récupérer le contenu de la page HTML
        response = requests.get(url)

    # Vérifier si la requête a réussi (statut 200)
        if response.status_code == 200:
            # Utiliser BeautifulSoup pour analyser le contenu HTML de la page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extraire la balise <title>
            title_tag = soup.title.text.strip() if soup.title else None

            # Extraire les balises <h1>, <h2>
            header_tags = [header.text.strip() for header in soup.find_all(['h1', 'h2'])]

            # Extraire les balises <b>, <em>
            bold_tags = [bold.text.strip() for bold in soup.find_all('b')]
            italic_tags = [italic.text.strip() for italic in soup.find_all('em')]

            # Extraire les liens (balises <a>)
            link_tags = soup.find_all('a')
            links = [link.get('href') for link in link_tags if link.get('href')]

            # Stocker les informations dans MongoDB
            scraped_document = {
                "url": url, "html":response.text,
                "title": title_tag,
                "header_tags": header_tags,
                "bold_tags": bold_tags,
                "italic_tags": italic_tags,
                "links": links
            }

            db.insert_one(scraped_document)
            print("Informations extraites et stockées dans la base de données.")
        else:
            print(f"Échec de la récupération de la page. Code d'état : {response.status_code}")
    else:
        print("Aucune URL en attente de traitement.")



# Exemple d'utilisation
while True:
    # Récupère une URL en attente de traitement depuis la base de données
    url_a_traiter = get_pending_url(collection)

    if url_a_traiter:
        # Traite l'URL
        simple_scrape(collection, url_a_traiter)

        # Marque l'URL comme traitée dans la base de données
        set_url_completed(collection, url_a_traiter)
    else:
        # Si aucune URL en attente n'est trouvée, sort de la boucle
        break
