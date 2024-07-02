from datetime import datetime
import pymongo
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .database import urls_collection, pages_metadata_collection
from logs.logs import log_error, log_event


def insert_url(db, url, scope, status):
    """
    Insère une nouvelle URL dans la base de données avec le statut donné.

    Args:
    - db (pymongo.Database): Base de données MongoDB.
    - url (str): URL à insérer.
    - scope (str): Scope auquel l'URL appartient.
    - status (str): Statut initial de l'URL ("pending", "processing", "completed", etc.).

    Returns:
    - None
    """
    new_url = {
        'url': url,
        'scope': scope,
        'status': status,
        'attempts': 0,
        'last_attempt': None
    }
    try:
        db.update_one({'url': url}, {"$setOnInsert": new_url}, upsert=True)
        log_event(f"Nouvelle URL insérée dans la base de données : {url}")
    except pymongo.errors.DuplicateKeyError:
        log_event(f"L'URL existe déjà dans la base de données : {url}")
    except Exception as e:
        log_error(url, f"Erreur d'insertion : {e}")


def get_pending_url(db):
    """
    Récupère une URL en attente de traitement depuis la base de données et met à jour son statut à "processing".

    Args:
    - db (pymongo.Database): Base de données MongoDB.

    Returns:
    - dict: Document de l'URL récupérée, ou None si aucune URL en attente.
    """
    try:
        url_doc = db.find_one_and_update(
            {"status": "pending"},
            {"$set": {"status": "processing", "last_attempt": datetime.now()}},
            return_document=pymongo.ReturnDocument.BEFORE
        )
        if url_doc:
            log_event(f"URL en attente récupérée pour traitement : {url_doc['url']}")
        return url_doc
    except Exception as e:
        log_error("Opération BD", f"Erreur lors de la récupération de l'URL en attente : {e}")
        return None


def set_url_completed(db, url):
    """
    Met à jour le statut d'une URL dans la base de données à "completed".

    Args:
    - db (pymongo.Database): Base de données MongoDB.
    - url (dict): Document de l'URL à marquer comme complétée.

    Returns:
    - None
    """
    try:
        db.update_one(
            {"_id": url["_id"]},
            {"$set": {"status": "completed"}}
        )
        log_event(f"Statut de l'URL mis à complété : {url['url']}")
    except Exception as e:
        log_error(url["url"], f"Erreur lors de la mise à jour du statut de l'URL à complété : {e}")


def scrape_page(url_doc):
    """
    Récupère le contenu HTML d'une page à partir de son URL.

    Args:
    - url_doc (dict): Document de l'URL contenant l'URL à récupérer.

    Returns:
    - str: Contenu HTML de la page récupérée, ou None en cas d'erreur de requête.
    """
    url = url_doc["url"]
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        log_event(f"Page récupérée avec succès : {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        log_error(url, f"Erreur de requête : {e}")
        return None


def extract_links(html, scope):
    """
    Extrait tous les liens valides d'une page HTML en fonction d'un scope donné.

    Args:
    - html (str): Contenu HTML de la page.
    - scope (str): Scope à partir duquel extraire les liens.

    Returns:
    - list: Liste des URLs complètes des liens extraits.
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = [urljoin(scope, a['href']) for a in soup.find_all('a', href=True) if a['href'].startswith(scope)]
    return links


def extract_metadata(html):
    """
    Extrait les métadonnées pertinentes d'une page HTML.

    Args:
    - html (str): Contenu HTML de la page.

    Returns:
    - tuple: Tuple contenant les listes des titres, textes en gras, textes en fort et textes en italique trouvés sur la page.
    """
    soup = BeautifulSoup(html, 'html.parser')

    titles = [soup.title.string] if soup.title else []
    titles.extend([h.get_text() for h in soup.find_all(['h1', 'h2'])])

    bold_texts = [b.get_text() for b in soup.find_all('b')]
    strong_texts = [strong.get_text() for strong in soup.find_all('strong')]
    em_texts = [em.get_text() for em in soup.find_all('em')]

    return titles, bold_texts, strong_texts, em_texts


def save_page(db, url, html, titles, bold_texts, strong_texts, em_texts):
    """
    Enregistre les données de la page dans la base de données.

    Args:
    - db (pymongo.Database): Base de données MongoDB.
    - url (str): URL de la page.
    - html (str): Contenu HTML de la page.
    - titles (list): Liste des titres de la page.
    - bold_texts (list): Liste des textes en gras de la page.
    - strong_texts (list): Liste des textes en fort de la page.
    - em_texts (list): Liste des textes en italique de la page.

    Returns:
    - None
    """
    page_doc = {
        "url": url,
        "html": html,
        "titles": titles,
        "bold_texts": bold_texts,
        "strong_texts": strong_texts,
        "em_texts": em_texts,
        "scraping_date": datetime.now()
    }
    try:
        db.insert_one(page_doc)
        log_event(f"URL {url} récupérée et sauvegardée avec succès.")
    except Exception as e:
        log_error(url, f"Erreur lors de la sauvegarde des données de la page : {e}")


def simple_scrape(db, url_doc, max_urls, processed_count):
    """
    Fonction principale de scraping qui récupère et traite une page, extrait ses métadonnées et ses liens.

    Args:
    - db (dict): Dictionnaire contenant les collections MongoDB 'urls' et 'pages_metadata'.
    - url_doc (dict): Document de l'URL à traiter.
    - max_urls (int): Nombre maximum d'URLs à traiter.
    - processed_count (int): Nombre d'URLs déjà traitées.

    Returns:
    - int: Nombre total d'URLs traitées après le traitement de l'URL actuelle.
    """
    if processed_count >= max_urls:
        return processed_count

    html = scrape_page(url_doc)
    if not html:
        set_url_completed(db['urls'], url_doc)
        return processed_count

    titles, bold_texts, strong_texts, em_texts = extract_metadata(html)
    save_page(db['pages_metadata'], url_doc['url'], html, titles, bold_texts, strong_texts, em_texts)

    new_links = extract_links(html, url_doc['scope'])
    for link in new_links:
        if processed_count >= max_urls:
            break
        if not db['urls'].find_one({"url": link}):
            insert_url(db['urls'], link, url_doc['scope'], "pending")
            processed_count += 1

    set_url_completed(db['urls'], url_doc)
    processed_count += 1  # Incrémente après avoir traité l'URL avec succès

    return processed_count
