import argparse
from scraper.database import urls_collection
from scraper.scraper import insert_url

EXAMPLE_URL = "https://www.lelibrepenseur.org/categorie/llp-theque/conferences/"
EXAMPLE_SCOPE = "https://www.lelibrepenseur.org"

def add_initial_url(url: str, scope: str) -> None:
    """
    Insère une URL initiale dans la base de données avec le statut "pending".

    Args:
    - url (str): L'URL à ajouter.
    - scope (str): Le scope auquel l'URL appartient.

    Returns:
    - None
    """
    insert_url(urls_collection, url, scope, "pending")
    print(f"Ajout de l'URL {url} avec le scope {scope} à la base de données.")

def show_example_usage() -> None:
    """
    Affiche un exemple d'utilisation pour ajouter une URL initiale.
    """
    print(f"Exemple d'utilisation : add_initial_url('{EXAMPLE_URL}', '{EXAMPLE_SCOPE}')")

def main():
    """
    Fonction principale pour gérer les arguments en ligne de commande et ajouter l'URL initiale à la base de données.
    """
    parser = argparse.ArgumentParser(description="Ajouter une URL et un scope à la base de données")
    parser.add_argument("url", type=str, nargs='?', help="L'URL initiale à scraper")
    parser.add_argument("scope", type=str, nargs='?', help="Le scope des URLs à scraper")

    args = parser.parse_args()

    if not args.url or not args.scope:
        show_example_usage()
    else:
        add_initial_url(args.url, args.scope)

if __name__ == "__main__":
    main()
