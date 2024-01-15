import time
from requests.exceptions import RequestException
from multiprocessing import Process
from database.connection_bdd import url_en_attente, collection
from logs.logs import log_error, log_event
from scraper.scraper_simple import get_pending_url, simple_scrape, set_url_completed


def add_initial_url(url, scope):
    new_document = {'url': url, 'scope': scope, 'status': 'pending'}
    url_en_attente.insert_one(new_document)


# Ajouter l'URL initiale
add_initial_url('https://quotes.toscrape.com/page/2/', 'https://quotes.toscrape.com')


def distributed_scraper(base_url, process_id):
    max_retries = 5
    retry_delay = 60  # seconds

    while True:
        # Récupère une URL en attente de traitement depuis la base de données
        url_a_traiter = get_pending_url(url_en_attente)

        if url_a_traiter:
            # Check if the URL has not been processed or is not in the main collection
            if not collection.find_one({"url": url_a_traiter}):
                retries = 0

                while retries < max_retries:
                    try:
                        # Process the URL
                        simple_scrape(collection, base_url, url_a_traiter)
                        # Mark the URL as completed in 'pending_urls'
                        set_url_completed(url_en_attente, url_a_traiter)
                        break  # Break out of the retry loop if successful
                    except RequestException as e:
                        # Handle request-related exceptions (e.g., network issues, timeouts)
                        log_error(url_a_traiter, f"Error processing URL: {e}")
                        retries += 1
                        time.sleep(retry_delay)  # Introduce a delay before retrying
                        log_event(f"Retrying... Attempt {retries}/{max_retries}")
                    except Exception as e:
                        # Handle other exceptions
                        log_error(url_a_traiter, f"Unexpected error: {e}")
                        # Mark the URL as completed to avoid repeated attempts
                        set_url_completed(url_en_attente, url_a_traiter)
                        break  # Break out of the retry loop

                if retries == max_retries:
                    # If maximum retries reached, mark the URL as completed
                    log_event(f"Maximum retries reached for URL: {url_a_traiter}")
                    set_url_completed(url_en_attente, url_a_traiter)
        else:
            # Si aucune URL en attente n'est trouvée, sort de la boucle
            break


# Démarrez plusieurs processus de scraping
num_processes = 3  # You can adjust the number of processes based on your requirements
processes = []

for i in range(num_processes):
    process = Process(target=distributed_scraper, args=('https://quotes.toscrape.com', i))
    processes.append(process)
    process.start()

# Attend que tous les processus se terminent
for process in processes:
    process.join()
