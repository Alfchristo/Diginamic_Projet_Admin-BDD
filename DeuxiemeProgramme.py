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


def get_pending_url(db):
    url_document = db.find_one_and_update({"status": "pending"},
                                          {"$set": {"status": "processing"}},
                                          return_document=pymongo.ReturnDocument.BEFORE
                                          )
    if url_document:
        return url_document["url"]
    else:
        # Si aucune URL en attente n'est trouvée dans la collection 'urls', essayez depuis 'pending_urls'
        pending_urls_collection = database['pending_urls']
        pending_url_document = pending_urls_collection.find_one_and_update({"status": "pending"},
                                                                           {"$set": {"status": "processing"}},
                                                                           return_document=pymongo.ReturnDocument.BEFORE
                                                                           )
        if pending_url_document:
            return pending_url_document["url"]
        else:
            return None


def set_url_completed(db, url):
    # Marque l'URL comme traitée dans la base de données
    db.update_one({"url": url}, {"$set": {"status": "completed"}})


def simple_scrape(db, base_url, url):
    # Créer la collection 'pending_urls' si elle n'existe pas encore
    pending_urls_collection = database['pending_urls']

    if url:
        # Make the URL absolute by combining it with the base URL
        absolute_url = urljoin(base_url, url)

        # Check if the URL has been processed or is already in the pending_urls collection
        if not collection.find_one({"url": url}) and not pending_urls_collection.find_one({"url": url}):
            # Process the URL
            simple_scrape(collection, 'https://quotes.toscrape.com', url_a_traiter)
            # Mark the URL as completed in 'pending_urls'
            set_url_completed(pending_urls_collection, url_a_traiter)

        # Récupérer le contenu de la page HTML
        print("Processing URL:", absolute_url)
        response = requests.get(absolute_url)

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

            # Extraire les liens (balises <a>) et les ajouter à la collection 'pending_urls'
            link_tags = soup.find_all('a')
            new_links = [urljoin(absolute_url, link.get('href')) for link in link_tags if link.get('href')]

            for new_link in new_links:
                # Check if the link is not already in the 'pending_urls' collection
                if not pending_urls_collection.find_one({"url": new_link}):
                    # Add the link to the 'pending_urls' collection
                    pending_urls_collection.insert_one({"url": new_link, "status": "pending"})

            # Stocker les informations dans MongoDB
            scraped_document = {
                "url": url, "html": response.text,
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


simple_scrape(pending_urls_collection, 'https://quotes.toscrape.com', new_document['url'])

# Mark the URL as completed
set_url_completed(pending_urls_collection, new_document['url'])
# Exemple d'utilisation
while True:
    # Récupère une URL en attente de traitement depuis la base de données
    url_a_traiter = get_pending_url(collection)

    if url_a_traiter:
        # Check if the URL has not been processed or is not in the main collection
        if not collection.find_one({"url": url_a_traiter}):
            # Process the URL
            simple_scrape(collection, 'https://quotes.toscrape.com', url_a_traiter)
            # Mark the URL as completed in 'pending_urls'
            set_url_completed(pending_urls_collection, url_a_traiter)
    else:
        # Si aucune URL en attente n'est trouvée, sort de la boucle
        break
