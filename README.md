# SEO Web Scraper

Ce projet est un scraper web conçu à des fins de SEO. Il vous permet de récupérer des pages web, d'extraire leur contenu pertinent et de stocker les données dans une base de données MongoDB. Le scraper prend en charge le scraping distribué, les tentatives de reprise en cas d'échec et est configurable via une interface en ligne de commande.
## Fonctionnalités

- Récupération de pages web et extraction de contenu tel que les titres, en-têtes, textes en gras et en italique.- Follow links on the scraped pages and continue scraping within a specified scope.
- Suivi des liens sur les pages scrapées et continuation du scraping dans un périmètre spécifié.- Configure the maximum number of URLs to scrape.
- Prévention des entrées d'URL dupliquées dans la base de données.
- Configuration du nombre maximum d'URLs à scraper.
- Retentatives des requêtes échouées jusqu'à un nombre spécifié de fois.
- Utilisation d'une base de données MongoDB pour stocker les URLs, le contenu des pages et les journaux.
- Interface en ligne de commande pour ajouter des URLs à la base de données et démarrer le scraper.
  
## Prérequis

- Python 3.x
- MongoDB

## Installation

1. Clonez le dépôt :
    ```sh
    git clone https://github.com/Diginamic-M09-Gr3/32123BC5-Admin-BDD.git
    cd 32123BC5-Admin-BDD
    ```

2. Installez les packages Python requis :
    ```sh
    pip install -r requirements.txt
    ```

3. Assurez-vous que MongoDB est installé et en cours d'exécution sur votre machine.

## Utilisation
### - **Utilisation de cli.py**:
```sh
 python cli.py --help
   ``` 
#### Ajout d'une URL à la Base de Données

Pour ajouter une URL initiale à la base de données, utilisez la commande add_url avec l'URL et le périmètre comme arguments :
```sh
  python cli.py add_url "https://example.com" "https://example.com/scope"
   ```
#### Démarrage du Scraper
Pour démarrer le processus de scraping, utilisez la commande scrape avec un argument optionnel pour spécifier le nombre maximum d'URLs à scraper :
```sh
 python cli.py scrape --max_urls 20
   ``` 

### - **- Utilisation de scripts .py**:
#### Ajout d'URLs
```sh
python add_url.py <URL> <SCOPE>
```
#### Exécution du Scraper
```sh
python main.py [max_urls]
max_urls : Optionnel. Le nombre maximum d'URLs à scraper. Par défaut, 10 s'il n'est pas spécifié.
```

## Exemple
```sh
python add_url.py https://example.com https://example.com
python main.py 50
```

## Structure du Projet
- **scraper/**: Contient la logique principale du scraper, la connexion à la base de données et les fonctions de journalisation.
- **cli.py**: Interface en ligne de commande pour ajouter des URLs et démarrer le scraper.
- **main.py**: Script principal pour exécuter le scraper avec des arguments optionnels.
   
## Configuration

### MongoDB
Assurez-vous que vos paramètres de connexion MongoDB dans scraper/database.py sont corrects. Par défaut, la connexion est établie avec une instance MongoDB locale :
```sh
client = MongoClient('mongodb://localhost:27017/')
database = client['projetseo']
urls_collection = database['urls']
```
### Journalisation
Les fonctions de journalisation sont définies dans scraper/logs.py. Mettez à jour ces fonctions pour personnaliser le comportement de la journalisation.

## Schéma de la Base de Données MongoDB
### Nom de la Base de Données : projetseo
**Collections** :
1. *urls*
   - **`_id`** : ObjectId (généré automatiquement)
   - **`url`** : chaîne de caractères (URL de la page)
   - **`scope`** : chaîne de caractères (périmètre des URLs à scraper)
   - **`status`** : chaîne de caractères ("pending", "processing", "completed", etc.)
   - **`attempts`** : entier (nombre de tentatives de scraping)
   - **`last_attempt`** : date-heure (dernière tentative de scraping)
   
2. *pages_metadata*:
   - **`_id`** : ObjectId (généré automatiquement)
   - **`url`** : chaîne de caractères (URL de la page)
   - **`html`** : chaîne de caractères (contenu HTML de la page)
   - **`titles`** : tableau de chaînes de caractères (titres extraits de la page)
   - **`bold_texts`** : tableau de chaînes de caractères (textes en gras extraits de la page)
   - **`strong_texts`** : tableau de chaînes de caractères (textes en fort extraits de la page)
   - **`em_texts`** : tableau de chaînes de caractères (textes en italique extraits de la page)
   - **`scraping_date`** : date-heure (date et heure du scraping de la page)

3. *logs*:
- **`_id`** : ObjectId (généré automatiquement)
- **`timestamp`** : date-heure (date et heure du log)
- **`level`** : chaîne de caractères (niveau du log, par exemple : "INFO", "ERROR", "WARNING")
- **`message`** : chaîne de caractères (message du log)

### Collaborateurs
- Alfred Christopher
- Berrabah Fatima
- Cormerais Dorian
- Mougani Christ
