import argparse
from multiprocessing import Process
from database.connection_bdd import url_en_attente, collection
from scraper.scraper_simple import get_pending_url, simple_scrape, set_url_completed


def add_initial_url(url, scope):
    new_document = {'url': url, 'scope': scope, 'status': 'pending'}
    url_en_attente.insert_one(new_document)


def distributed_scraper(base_url, process_id):
    while True:
        url_a_traiter = get_pending_url(url_en_attente)
        if url_a_traiter:
            if not collection.find_one({"url": url_a_traiter}):
                simple_scrape(collection, base_url, url_a_traiter)
                set_url_completed(url_en_attente, url_a_traiter)
        else:
            break


def main():
    parser = argparse.ArgumentParser(description='Distributed Web Scraper')
    parser.add_argument('--url', required=True, help='Initial URL to start scraping')
    parser.add_argument('--scope', required=True, help='Scope of URLs to consider')
    parser.add_argument('--processes', type=int, default=3, help='Number of scraping processes')

    args = parser.parse_args()

    # Add the initial URL
    add_initial_url(args.url, args.scope)

    # Start multiple scraping processes
    processes = []
    for i in range(args.processes):
        process = Process(target=distributed_scraper, args=(args.url, i))
        processes.append(process)
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()


if __name__ == "__main__":
    main()
