import time
import requests
from scraper.database import urls_collection, database
from scraper.scraper import get_pending_url, simple_scrape, set_url_completed
from logs.logs import log_error, log_event

def main(max_urls=10, progress_callback=None):
    """
    Fonction principale pour traiter les URLs en attente jusqu'à un maximum donné.

    Args:
    - max_urls (int): Nombre maximum d'URLs à traiter. Par défaut, 10.
    - progress_callback (function, optional): Fonction de rappel pour mettre à jour la progression.

    Returns:
    - None
    """
    max_retries = 5
    retry_delay = 60  # secondes
    processed_count = 0

    while processed_count < max_urls:
        url_doc = get_pending_url(urls_collection)

        if url_doc:
            retries = 0
            while retries < max_retries:
                try:
                    processed_count = simple_scrape(database, url_doc, max_urls, processed_count)
                    if progress_callback:
                        progress_callback(1)  # Update the progress bar by 1
                    if processed_count >= max_urls:
                        break
                    set_url_completed(urls_collection, url_doc)
                    break  # Sortir de la boucle de réessai en cas de succès
                except requests.exceptions.RequestException as e:
                    log_error(url_doc['url'], f"Erreur de requête : {e}")
                    retries += 1
                    if retries < max_retries:
                        time.sleep(retry_delay)
                        log_event(f"Nouvelle tentative... Essai {retries}/{max_retries} pour l'URL : {url_doc['url']}")
                except Exception as e:
                    log_error(url_doc['url'], f"Erreur inattendue : {e}")
                    set_url_completed(urls_collection, url_doc)
                    break  # Sortir de la boucle de réessai en cas d'erreur inattendue

            if retries == max_retries:
                log_event(f"Nombre maximum de tentatives atteint pour l'URL : {url_doc['url']}")
                set_url_completed(urls_collection, url_doc)

        else:
            log_event("Aucune URL en attente trouvée. En attente...")
            time.sleep(10)  # Pause avant de vérifier les nouvelles URLs en attente

        log_event(f"{processed_count}/{max_urls} URLs traitées jusqu'à présent.")

    log_event(f"Traitement terminé de {max_urls} URLs.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        max_urls = int(sys.argv[1])
    else:
        max_urls = 10
    main(max_urls)
