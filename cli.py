import argparse
import logging
import sys

from colorama import Fore, Style, init
from tqdm import tqdm

from main import main as scrape_main  # Importer la fonction principale de scraping
from add_url import add_initial_url, show_example_usage  # Importer les fonctions de gestion des URLs

# Initialisation de colorama pour une sortie console colorée
init(autoreset=True)


def setup_logging():
    """
    Configuration du système de logs.
    """
    logging.basicConfig(level=logging.INFO, format=f'%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)

def add_url_command(url: str, scope: str) -> None:
    """
    Gestionnaire de commande pour ajouter une URL initiale pour le scraping.

    Args:
    - url (str): URL initiale à scraper.
    - scope (str): Scope des URLs à scraper.

    Returns:
    - None
    """
    if not url or not scope:
        show_example_usage()  # Afficher l'exemple d'utilisation si l'URL ou le scope est manquant
        return

    try:
        add_initial_url(url, scope)  # Appeler la fonction pour ajouter l'URL initiale
        logging.info(f"{Fore.GREEN}URL '{url}' ajoutée avec le scope '{scope}'.")
    except Exception as e:
        logging.error(f"{Fore.RED}Échec de l'ajout de l'URL '{url}' : {e}")


def scrape_command(max_urls: int) -> None:
    """
    Gestionnaire de commande pour démarrer le processus de scraping.

    Args:
    - max_urls (int): Nombre maximum d'URLs à scraper.

    Returns:
    - None
    """
    try:
        with tqdm(total=max_urls, desc="Progression du scraping",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                  leave=True, ncols=100) as pbar:
            scrape_main(max_urls=max_urls, progress_callback=pbar.update)  # Pass the progress_callback to scrape_main
        logging.info(f"{Fore.GREEN}Scraping démarré avec max_urls={max_urls}.")
    except Exception as e:
        logging.error(f"{Fore.RED}Échec du démarrage du scraping : {e}")


def parse_args() -> argparse.Namespace:
    """
    Analyser les arguments de la ligne de commande.

    Returns:
    - argparse.Namespace: Arguments analysés.
    """
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}SEO Scraper CLI{Style.RESET_ALL}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_url_parser = subparsers.add_parser("add_url",
                                           help=f"{Fore.YELLOW}Ajouter une URL pour commencer le scraping{Style.RESET_ALL}")
    add_url_parser.add_argument("url", type=str, nargs='?',
                                help=f"{Fore.YELLOW}L'URL initiale à scraper{Style.RESET_ALL}")
    add_url_parser.add_argument("scope", type=str, nargs='?',
                                help=f"{Fore.YELLOW}Le scope des URLs à scraper{Style.RESET_ALL}")

    scrape_parser = subparsers.add_parser("scrape",
                                          help=f"{Fore.YELLOW}Démarrer le processus de scraping{Style.RESET_ALL}")
    scrape_parser.add_argument("--max_urls", type=int, default=10,
                               help=f"{Fore.YELLOW}Nombre maximum d'URLs à scraper{Style.RESET_ALL}")

    return parser.parse_args()


def main_cli() -> None:
    """
    Fonction principale de l'application CLI.
    """
    setup_logging()  # Configuration des logs

    args = parse_args()  # Analyser les arguments de la ligne de commande

    if args.command == "add_url":
        add_url_command(args.url, args.scope)  # Gérer la commande add_url
    elif args.command == "scrape":
        scrape_command(args.max_urls)  # Gérer la commande scrape


if __name__ == "__main__":
    main_cli()  # Point d'entrée de l'application CLI
